module chain_stage_b (
    input  wire in0,
    input  wire in1,
    input  wire in2,
    output wire out0,
    output wire out1,
    output wire out2
);
  assign out0 = ~in0;
  assign out1 = in1 ^ in2;
  assign out2 = in0 | in2;
endmodule
