module fanin_reduce12 (
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
    output wire [15:0] out_word
);
    assign out_word = in0 ^ in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8 ^ in9 ^ in10 ^ in11;
endmodule
