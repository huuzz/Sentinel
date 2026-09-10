import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { StatusCard } from "../components/status-card";
import "./setup";

describe("StatusCard", () => {
  it("shows a healthy backend", () => {
    render(<StatusCard state={{ status: "ok", service: "sentinel-backend" }} />);
    expect(screen.getByText("Operational")).toBeInTheDocument();
    expect(screen.getByText("sentinel-backend")).toBeInTheDocument();
  });

  it("shows an unavailable backend", () => {
    render(<StatusCard state={null} />);
    expect(screen.getByText("Unavailable")).toBeInTheDocument();
  });
});
