module pattern_gen (
    input wire clk,
    input wire rst_n,
    input wire [15:0] seed,
    input wire [7:0] step,
    output reg [15:0] pattern
);
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            pattern <= 16'h1C3D;
        end else begin
            pattern <= {pattern[14:0], pattern[15] ^ step[0]} + seed + {8'h00, step};
        end
    end
endmodule
