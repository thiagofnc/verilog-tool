module gate_cloud (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [15:0] d,
    output wire [15:0] y
);
    wire [15:0] n0;
    wire [15:0] n1;
    wire [15:0] n2;

    assign n0 = (a & b) | (c ^ d);
    assign n1 = (a ^ c) + (b | d);
    assign n2 = {n0[7:0], n1[15:8]} ^ 16'h33CC;
    assign y = n0 ^ n1 ^ n2;
endmodule
