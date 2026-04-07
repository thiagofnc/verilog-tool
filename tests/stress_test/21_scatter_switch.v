module scatter_switch (
    input wire [15:0] src0,
    input wire [15:0] src1,
    input wire [15:0] src2,
    input wire [15:0] src3,
    input wire [2:0] sel,
    output reg [15:0] out_word
);
    always @(*) begin
        case (sel)
            3'b000: out_word = src0;
            3'b001: out_word = src1;
            3'b010: out_word = src2;
            3'b011: out_word = src3;
            3'b100: out_word = src0 ^ src2;
            3'b101: out_word = src1 + src3;
            3'b110: out_word = {src2[7:0], src0[15:8]};
            default: out_word = (src0 & src1) | (src2 ^ src3);
        endcase
    end
endmodule
