module status_flags (
    input wire clk,
    input wire rst_n,
    input wire [15:0] sample0,
    input wire [15:0] sample1,
    input wire [15:0] sample2,
    input wire pulse_in,
    output reg [7:0] flags,
    output reg irq
);
    reg sticky_zero;

    always @(sample0 or sample1 or sample2 or pulse_in) begin
        sticky_zero = (sample0 == 16'h0000) | (sample1 == 16'h0000) | (sample2 == 16'h0000);
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            flags <= 8'h00;
            irq <= 1'b0;
        end else begin
            flags[0] <= ^sample0;
            flags[1] <= &sample1;
            flags[2] <= |sample2;
            flags[3] <= pulse_in;
            flags[4] <= sticky_zero;
            flags[5] <= sample0[15] ^ sample1[15];
            flags[6] <= sample1[0] | sample2[0];
            flags[7] <= sample2[15] & sample0[0];
            irq <= pulse_in | sticky_zero | (&sample0[3:0]);
        end
    end
endmodule
