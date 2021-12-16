package plecoptera

import (
	"context"
	"encoding/json"
	"net/http"

	"github.com/go-logr/logr"
	"github.com/pkg/errors"
)

type estimateCostRequest struct {
	ParameterValues ParameterValues `json:"parameter_values"`
}

type estimateCostResponse struct {
	Cost float64 `json:"cost"`
}

type server struct {
	httpServer *http.Server
	estimator  *costEstimator
	logger     logr.Logger
}

func (s *server) estimateCostHandler(w http.ResponseWriter, r *http.Request) {
	// TODO: middleware
	logger := s.annotateLogger(r)

	logger.V(0).Info("request handling started")

	defer func() {
		if err := r.Body.Close(); err != nil {
			logger.Error(err, "request body close")
		}
	}()

	statusCode, err := s.estimateCost(logger, w, r)
	w.WriteHeader(statusCode)
	if err != nil {
		logger.Error(err, "request handling finished")
	} else {
		logger.V(0).Info("request handling finished")
	}
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

	response := &estimateCostResponse{Cost: cost}
	encoder := json.NewEncoder(w)
	if err := encoder.Encode(response); err != nil {
		return http.StatusInternalServerError, errors.Wrap(err, "json encode")
	}

	return http.StatusOK, nil
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

func newServer(logger logr.Logger, estimator *costEstimator) *server {
	handler := http.NewServeMux()

	srv := &server{
		httpServer: &http.Server{Handler: handler},
		estimator:  estimator,
		logger:     logger,
	}

	handler.HandleFunc("/estimate_cost", srv.estimateCostHandler)

	go func() {
		if err := srv.httpServer.ListenAndServe(); err != http.ErrServerClosed {
			srv.logger.Error(err, "http server listen and serve")
		}
	}()

	return srv
}
