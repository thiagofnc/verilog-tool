module async_capture (
    input wire clk,
    input wire rst_n,
    input wire async_a,
    input wire async_b,
    output reg capture
);
    reg sync0;
    reg sync1;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sync0 <= 1'b0;
            sync1 <= 1'b0;
            capture <= 1'b0;
        end else begin
            sync0 <= async_a ^ async_b;
            sync1 <= sync0;
            capture <= sync0 & ~sync1;
        end
    end
endmodule
