module checksum_merge (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [15:0] d,
    output wire [15:0] checksum
);
    assign checksum = a + {b[7:0], b[15:8]} + (c ^ 16'h0F0F) + (d ^ 16'hF0F0);
endmodule
