module clock_div (
    input wire clk,
    input wire rst_n,
    output reg slow_clk
);
    reg [3:0] div_count;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            div_count <= 4'b0000;
            slow_clk <= 1'b0;
        end else begin
            div_count <= div_count + 4'b0001;
            if (div_count == 4'b1001) begin
                slow_clk <= ~slow_clk;
                div_count <= 4'b0000;
            end
        end
    end
endmodule
