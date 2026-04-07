module bus_twister (
    input wire [15:0] a,
    input wire [15:0] b,
    input wire [15:0] c,
    input wire [1:0] sel,
    output reg [15:0] y
);
    always @(*) begin
        case (sel)
            2'b00: y = {a[7:0], b[15:8]} ^ c;
            2'b01: y = (a & b) | {c[3:0], a[15:4]};
            2'b10: y = (a + c) ^ {b[0], b[15:1]};
            default: y = {c[5:0], a[15:6]} + (b ^ 16'h55AA);
        endcase
    end
endmodule
