module wide_control (
    input wire [15:0] in0,
    input wire [15:0] in1,
    input wire [15:0] in2,
    input wire [15:0] in3,
    input wire [15:0] in4,
    input wire [15:0] in5,
    input wire [15:0] in6,
    input wire [15:0] in7,
    input wire [15:0] in8,
    input wire [15:0] in9,
    input wire [15:0] in10,
    input wire [15:0] in11,
    input wire [15:0] in12,
    input wire [15:0] in13,
    input wire [7:0] mode,
    output reg [15:0] ctrl_out
);
    always @(*) begin
        ctrl_out = (in0 ^ in4 ^ in8 ^ in12)
                 + (in1 & in5)
                 + (in2 | in6)
                 + (in3 ^ in7)
                 + (in9 + in10)
                 + (in11 ^ in13)
                 + {8'h00, mode};
    end
endmodule
