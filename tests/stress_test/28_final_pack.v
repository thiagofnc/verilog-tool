module final_pack (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [15:0] d,
    output reg [15:0] pack
);
    always @(*) begin
        pack[3:0] = a[3:0] ^ b[3:0];
        pack[7:4] = c[7:4] + d[7:4];
        pack[11:8] = (a[11:8] & c[11:8]) | b[11:8];
        pack[15:12] = d[15:12] ^ a[15:12] ^ c[15:12];
    end
endmodule
