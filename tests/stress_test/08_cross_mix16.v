module cross_mix16 (
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
    input wire [15:0] in14,
    input wire [15:0] in15,
    input wire [3:0] sel,
    output reg [15:0] mix_out
);
    always @(*) begin
        case (sel)
            4'h0: mix_out = in0 + in5 + in10 + in15;
            4'h1: mix_out = in1 ^ in6 ^ in11 ^ in12;
            4'h2: mix_out = (in2 & in7) | (in8 ^ in13);
            4'h3: mix_out = {in3[7:0], in14[15:8]} + in9;
            4'h4: mix_out = (in4 | in12) ^ (in0 + in8);
            4'h5: mix_out = (in5 + in6) ^ (in7 + in8);
            4'h6: mix_out = (in9 & in10) | (in11 ^ in12);
            4'h7: mix_out = {in13[3:0], in14[15:4]} + in15;
            4'h8: mix_out = in0 ^ in3 ^ in6 ^ in9 ^ in12 ^ in15;
            4'h9: mix_out = in1 + in4 + in7 + in10 + in13;
            4'hA: mix_out = in2 ^ in5 ^ in8 ^ in11 ^ in14;
            4'hB: mix_out = (in3 + in12) ^ (in6 | in15);
            4'hC: mix_out = (in4 & in9) + (in8 ^ in13);
            4'hD: mix_out = {in5[0], in10[15:1]} ^ in14;
            4'hE: mix_out = (in6 + in11) ^ (in1 & in7);
            default: mix_out = in0 ^ in1 ^ in2 ^ in3 ^ in4 ^ in5 ^ in6 ^ in7 ^ in8 ^ in9 ^ in10 ^ in11 ^ in12 ^ in13 ^ in14 ^ in15;
        endcase
    end
endmodule
