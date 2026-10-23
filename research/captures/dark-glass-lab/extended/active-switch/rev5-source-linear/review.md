# Source-only decoded-space filtering

- This was the predeclared source-only BT.709 alternative, not another color-space search. The output filter stayed in its accepted encoded space; one shared 23-coefficient material was recalibrated with unchanged optics, widths, source, shadow and masks.
- Direct versus cached output was bit-exact for both references. The original encoded-output material derivative was reused, with native comparisons deciding every proposed step.
- Six bounded steps ended at E ratios 1.00440825 / 1.00126168. Neither meets the required 0.995; original guards remain violated. Final gains were below 0.000001 in squared worst-ratio objective. No pass, image update or public implementation change.
- Along with the source+output failure, this does not support adopting this filtering convention. It does not establish that Apple filters in encoded space; remaining source, material and optical assumptions can confound that inference. Do not continue the same fit without new evidence.
