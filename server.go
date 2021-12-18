package plecoptera

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type server struct {
	httpServer *http.Server
	estimator  *costEstimator
	report     *Report
	logger     logr.Logger
}

// Estimate Cost

type estimateCostRequest struct {
	ParameterValues []*ParameterValue `json:"parameter_values"`
}

type estimateCostResponse struct {
	Cost float64 `json:"cost"`
}

func (s *server) estimateCostHandler(w http.ResponseWriter, r *http.Request) {
	s.middleware(w, r, s.estimateCost)
}

func (s *server) estimateCost(logger logr.Logger, w http.ResponseWriter, r *http.Request) (int, error) {
	if r.Method != http.MethodGet {
		return http.StatusMethodNotAllowed, errors.New("invalid method")
	}

	decoder := json.NewDecoder(r.Body)
	request := &estimateCostRequest{}
	err := decoder.Decode(request)
	if err != nil {
		return http.StatusBadRequest, errors.Wrap(err, "json decode")
	}

	ctx := logr.NewContext(r.Context(), logger)
	cost, err := s.estimator.estimateCost(ctx, request.ParameterValues)
	if err != nil {
		return http.StatusInternalServerError, errors.Wrap(err, "estimate cost")
	}

	logger.V(1).Info(
		"estimate cost",
		"parameter_values", request.ParameterValues,
		"cost", cost,
	)

	response := &estimateCostResponse{Cost: cost}
	encoder := json.NewEncoder(w)
	if err := encoder.Encode(response); err != nil {
		return http.StatusInternalServerError, errors.Wrap(err, "json encode")
	}

	return http.StatusOK, nil
}

// Register report

// registerReportRequest contains the output of RBFOpt
type registerReportRequest struct {
	Report *Report `json:"report"`
}

type registerReportResponse struct {
}

func (s *server) registerReportHandler(w http.ResponseWriter, r *http.Request) {
	s.middleware(w, r, s.registerReport)
}

func (s *server) registerReport(
	logger logr.Logger,
	w http.ResponseWriter,
	r *http.Request,
) (int, error) {
	if r.Method != http.MethodPost {
		return http.StatusMethodNotAllowed, errors.New("invalid method")
	}

	decoder := json.NewDecoder(r.Body)
	request := &registerReportRequest{}
	err := decoder.Decode(request)
	if err != nil {
		return http.StatusBadRequest, errors.Wrap(err, "json decode")
	}

	// simply cache the report
	logger.V(1).Info("report received", "report", request.Report)
	s.report = request.Report

	// response is empty, but for the sake of symmetry, fill it anyway
	response := &http.Response{}
	encoder := json.NewEncoder(w)
	if err := encoder.Encode(response); err != nil {
		return http.StatusInternalServerError, errors.Wrap(err, "json encode")
	}

	return http.StatusOK, nil
}

type handlerFunc func(logger logr.Logger, w http.ResponseWriter, r *http.Request) (int, error)

func (s *server) middleware(w http.ResponseWriter, r *http.Request, handler handlerFunc) {
	logger := s.annotateLogger(r)

	logger.V(0).Info("request handling started")

	defer func() {
		if err := r.Body.Close(); err != nil {
			logger.Error(err, "request body close")
		}
	}()

	statusCode, err := handler(logger, w, r)
	w.WriteHeader(statusCode)
	if err != nil {
		logger.Error(err, "request handling finished")
	} else {
		logger.V(0).Info("request handling finished")
	}
}

func (s *server) annotateLogger(r *http.Request) logr.Logger {
	return s.logger.WithValues(
		"url", r.URL,
		"method", r.Method,
		"remote_addr", r.RemoteAddr,
	)
}

func (s *server) quit() {
	if err := s.httpServer.Shutdown(context.Background()); err != nil {
		s.logger.Error(err, "http server shutdown")
	}
}

func newServer(logger logr.Logger, endpoint string, estimator *costEstimator) *server {
	handler := http.NewServeMux()

	srv := &server{
		httpServer: &http.Server{
			Addr:    endpoint,
			Handler: handler,
		},
		estimator: estimator,
		logger:    logger,
	}

	handler.HandleFunc("/estimate_cost", srv.estimateCostHandler)
	handler.HandleFunc("/register_report", srv.registerReportHandler)

	go func() {
		if err := srv.httpServer.ListenAndServe(); err != http.ErrServerClosed {
			srv.logger.Error(err, "http server listen and serve")
		}
	}()

	return srv
}
