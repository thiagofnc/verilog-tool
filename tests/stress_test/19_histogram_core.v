module histogram_core (
    input wire clk,
    input wire rst_n,
    input wire [15:0] sample,
    input wire [15:0] alt,
    output reg [15:0] hist_out
);
    reg [3:0] bins0;
    reg [3:0] bins1;
    reg [3:0] bins2;
    reg [3:0] bins3;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            bins0 <= 4'h0;
            bins1 <= 4'h0;
            bins2 <= 4'h0;
            bins3 <= 4'h0;
            hist_out <= 16'h0000;
        end else begin
            bins0 <= bins0 + sample[1:0] + alt[1:0];
            bins1 <= bins1 + sample[5:4] + alt[5:4];
            bins2 <= bins2 + sample[9:8] + alt[9:8];
            bins3 <= bins3 + sample[13:12] + alt[13:12];
            hist_out <= {bins3, bins2, bins1, bins0};
        end
    end
endmodule
