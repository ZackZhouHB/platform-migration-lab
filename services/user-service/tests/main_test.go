package main

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"
)

func TestHealthResponse(t *testing.T) {
	resp := HealthResponse{Status: "healthy", Service: "user-service", Version: "1.0.0"}
	if resp.Status != "healthy" {
		t.Errorf("expected healthy, got %s", resp.Status)
	}
	if resp.Service != "user-service" {
		t.Errorf("expected user-service, got %s", resp.Service)
	}
}

func TestUserJSON(t *testing.T) {
	user := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
	data, err := json.Marshal(user)
	if err != nil {
		t.Fatalf("failed to marshal user: %v", err)
	}
	var decoded User
	json.Unmarshal(data, &decoded)
	if decoded.Name != "Alice" {
		t.Errorf("expected Alice, got %s", decoded.Name)
	}
}

// Simple test runner for non-go-test environments
func main() {
	fmt.Println("User Service Tests")
	fmt.Println("──────────────────")
	// In practice, use `go test ./...`
	fmt.Println("  ✓ Run with: go test ./...")
	os.Exit(0)
}
