module multi_add (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [15:0] d,
    input wire [15:0] bias,
    output wire [15:0] sum
);
    assign sum = a + b + c + d + bias;
endmodule
