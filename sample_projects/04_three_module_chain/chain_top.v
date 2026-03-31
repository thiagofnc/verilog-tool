module chain_top (
    input  wire in0,
    input  wire in1,
    input  wire in2,
    output wire out0,
    output wire out1,
    output wire out2
);
  wire a_out0;
  wire a_out1;
  wire a_out2;
  wire b_out0;
  wire b_out1;
  wire b_out2;

  chain_stage_a u_stage_a (
      .in0(in0),
      .in1(in1),
      .in2(in2),
      .out0(a_out0),
      .out1(a_out1),
      .out2(a_out2)
  );

  chain_stage_b u_stage_b (
      .in0(a_out0),
      .in1(a_out1),
      .in2(a_out2),
      .out0(b_out0),
      .out1(b_out1),
      .out2(b_out2)
  );

  chain_stage_c u_stage_c (
      .in0(b_out0),
      .in1(b_out1),
      .in2(b_out2),
      .out0(out0),
      .out1(out1),
      .out2(out2)
  );
endmodule
