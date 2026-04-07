module window_filter (
    input wire clk,
    input wire rst_n,
    input wire [15:0] din,
    input wire [3:0] coeff,
    output reg [15:0] dout
);
    reg [15:0] d0;
    reg [15:0] d1;
    reg [15:0] d2;
    reg [15:0] d3;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            d0 <= 16'h0000;
            d1 <= 16'h0000;
            d2 <= 16'h0000;
            d3 <= 16'h0000;
            dout <= 16'h0000;
        end else begin
            d0 <= din;
            d1 <= d0;
            d2 <= d1;
            d3 <= d2;
            dout <= d0 + d1 + d2 + d3 + {12'h000, coeff};
        end
    end
endmodule
