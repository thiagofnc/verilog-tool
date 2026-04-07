module compare_mesh (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [15:0] d,
    output reg [15:0] cmp_out
);
    always @(*) begin
        cmp_out[0] = (a > b);
        cmp_out[1] = (a < b);
        cmp_out[2] = (c > d);
        cmp_out[3] = (c < d);
        cmp_out[7:4] = a[7:4] ^ d[7:4];
        cmp_out[11:8] = b[11:8] + c[11:8];
        cmp_out[15:12] = (a[15:12] & b[15:12]) | (c[15:12] ^ d[15:12]);
    end
endmodule
