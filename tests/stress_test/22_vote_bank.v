module vote_bank (
    input wire [15:0] in0,
    input wire [15:0] in1,
    input wire [15:0] in2,
    input wire [15:0] in3,
    input wire [15:0] in4,
    input wire [15:0] in5,
    output reg [15:0] vote_out
);
    integer i;
    reg [2:0] count;
    always @(*) begin
        for (i = 0; i < 16; i = i + 1) begin
            count = in0[i] + in1[i] + in2[i] + in3[i] + in4[i] + in5[i];
            vote_out[i] = (count >= 3);
        end
    end
endmodule
