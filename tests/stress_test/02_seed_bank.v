module seed_bank (
    input wire clk,
    input wire rst_n,
    input wire [15:0] in_a,
    input wire [15:0] in_b,
    input wire [7:0] mode,
    output reg [15:0] seed0,
    output reg [15:0] seed1,
    output reg [15:0] seed2,
    output reg [15:0] seed3
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            seed0 <= 16'h1357;
            seed1 <= 16'h2468;
            seed2 <= 16'hAAAA;
            seed3 <= 16'h5555;
        end else begin
            seed0 <= in_a ^ {8'h00, mode};
            seed1 <= in_b + {mode, 8'h01};
            seed2 <= {in_a[7:0], in_b[15:8]} ^ seed0;
            seed3 <= {in_b[3:0], in_a[15:4]} + seed1;
        end
    end
endmodule
