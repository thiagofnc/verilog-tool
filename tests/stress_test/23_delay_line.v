module delay_line (
    input wire clk,
    input wire rst_n,
    input wire [15:0] din,
    output reg [15:0] tap0,
    output reg [15:0] tap1
);
    reg [15:0] s0;
    reg [15:0] s1;
    reg [15:0] s2;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s0 <= 16'h0000;
            s1 <= 16'h0000;
            s2 <= 16'h0000;
            tap0 <= 16'h0000;
            tap1 <= 16'h0000;
        end else begin
            s0 <= din;
            s1 <= s0;
            s2 <= s1;
            tap0 <= s1;
            tap1 <= s2;
        end
    end
endmodule
