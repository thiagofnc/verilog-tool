module feedback_unit (
    input wire clk,
    input wire rst_n,
    input wire [15:0] forward_word,
    input wire [15:0] return_word,
    input wire enable,
    output reg [15:0] feedback_word
);
    reg [15:0] history;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            history <= 16'h3C5A;
            feedback_word <= 16'h0000;
        end else begin
            history <= forward_word ^ return_word ^ {15'b0, enable};
            if (enable) begin
                feedback_word <= (forward_word + history) ^ {return_word[4:0], return_word[15:5]};
            end else begin
                feedback_word <= forward_word ^ {history[0], history[15:1]};
            end
        end
    end
endmodule
