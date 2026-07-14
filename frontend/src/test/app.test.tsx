import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";

import App from "../App";
import { AuthProvider } from "../state/AuthContext";
import { queryClient } from "../state/queryClient";

describe("App", () => {
  it("renders landing headline", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>,
    );

    expect(screen.getByText(/AI Learning Assistant For Serious Students/i)).toBeInTheDocument();
  });
});
