package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"

	"github.com/redis/go-redis/v9"
)

type Transaction struct {
	OffsetName         string `json:"offset_name"`
	TransactionDate    string `json:"transaction_date"`
	Credit             int    `json:"credit"`
	TransactionDetails string `json:"transaction_details"`
	Source             string `json:"source"`
}

func connectRedis() *redis.Client {
	redisClient := redis.NewClient(&redis.Options{
		Addr:     "redis:6379",
		Password: "",
		DB:       0,
	})
	return redisClient
}

func getTransactionsFromRedis() ([]Transaction, error) {
	redisClient := connectRedis()
	defer redisClient.Close()
	ctx := context.Background()
	data, err := redisClient.Get(ctx, "transactions").Result()
	if err != nil {
		return nil, err
	}

	var transactions []Transaction
	err = json.Unmarshal([]byte(data), &transactions)
	if err != nil {
		return nil, err
	}

	return transactions, nil
}

func getTransactionsHandler(w http.ResponseWriter, r *http.Request) {
	transactions, err := getTransactionsFromRedis()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Get pagination parameters from the query string
	pageStr := r.URL.Query().Get("page")
	limitStr := r.URL.Query().Get("limit")

	// Set default values for pagination parameters
	page := 1
	limit := 10

	// Parse page and limt values from query parameters
	if pageStr != "" {
		page, err = strconv.Atoi(pageStr)
		if err != nil || page <= 0 {
			http.Error(w, "Invalid page value", http.StatusBadRequest)
			return
		}
	}
	if limitStr != "" {
		limit, err = strconv.Atoi(limitStr)
		if err != nil || limit <= 0 {
			http.Error(w, "Invalid limit value", http.StatusBadRequest)
			return
		}
	}

	// Calculate the start and end indices for the slice of transactions
	startIndex := (page - 1) * limit
	endIndex := startIndex + limit

	// Check for out-of-bounds slice index references
	if startIndex >= len(transactions) {
		http.Error(w, "Page does not contain any transactions", http.StatusBadRequest)
		return
	}
	if endIndex > len(transactions) {
		endIndex = len(transactions)
	}

	// Slice the transactions based on the calculated start and end indices
	paginatedTransactions := transactions[startIndex:endIndex]

	// Return the transactions as a JSON response
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(paginatedTransactions)
}

func searchTransactionsHandler(w http.ResponseWriter, r *http.Request) {
	transactions, err := getTransactionsFromRedis()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Get pagination parameters from the query string
	pageStr := r.URL.Query().Get("page")
	limitStr := r.URL.Query().Get("limit")
	queryDate := r.URL.Query().Get("transaction_date")
	queryCredit := r.URL.Query().Get("credit")
	queryDetails := r.URL.Query().Get("transaction_details")

	// Set default values for pagination parameters
	page := 1
	limit := 10

	// Parse page and limt values from query parameters
	if pageStr != "" {
		page, err = strconv.Atoi(pageStr)
		if err != nil || page <= 0 {
			http.Error(w, "Invalid page value", http.StatusBadRequest)
			return
		}
	}
	if limitStr != "" {
		limit, err = strconv.Atoi(limitStr)
		if err != nil || limit <= 0 {
			http.Error(w, "Invalid limit value", http.StatusBadRequest)
			return
		}
	}

	// Calculate the start and end indices for the slice of transactions
	startIndex := (page - 1) * limit
	endIndex := startIndex + limit

	var filteredTransactions []Transaction

	for _, t := range transactions {
		matches := true

		if queryDate != "" && t.TransactionDate != queryDate {
			matches = false
		}

		if queryCredit != "" {
			credit, err := strconv.Atoi(queryCredit)
			if err != nil || t.Credit != credit {
				matches = false
			}
		}

		if queryDetails != "" && !strings.Contains(strings.ToLower(t.TransactionDetails), strings.ToLower(queryDetails)) {
			matches = false
		}

		if matches {
			filteredTransactions = append(filteredTransactions, t)
		}
	}

	if len(filteredTransactions) == 0 {
		w.WriteHeader(http.StatusNotFound)
		w.Write([]byte("No matching transactions found"))
		return
	}

	// Check for out-of-bounds slice index references
	if startIndex >= len(filteredTransactions) {
		http.Error(w, "Page does not contain any transactions", http.StatusBadRequest)
		return
	}
	if endIndex > len(filteredTransactions) {
		endIndex = len(filteredTransactions)
	}

	// Slice the transactions based on the calculated start and end indices
	paginatedTransactions := transactions[startIndex:endIndex]

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(paginatedTransactions)
}

func main() {
	// Define HTTP routes
	http.HandleFunc("/api/transactions", getTransactionsHandler)
	http.HandleFunc("/api/transactions/search", searchTransactionsHandler)

	// Start the HTTP server
	fmt.Println("Server listening on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
