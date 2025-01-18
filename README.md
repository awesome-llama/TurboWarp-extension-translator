## TurboWarp extension translator

An experimental tool to convert some TurboWarp extensions into their Scratch block equivalent.

Most blocks in the following extensions are supported:

- lmscomments (More Comments)
- lmsutilsblocks (Lily's Toolbox)
- nkmoremotion (More Motion)
- nonameawacomparisons (More Comparisons)
- nonameawagraph (Graphics 2D)
- RixxyX (RixxyX)
- truefantommath (More Math)
- truefantomcouplers (Couplers)
- utilities (Utilities)


**WARNING: This tool only generates the `project.json` file.**
If named with .sb3, TurboWarp will be able to read it for convenience. Costumes and sounds are not preserved. 


### Caveats

- Does not account for behaviour in recursion. Scratch does not maintain variable scope within each run of a custom block, the variables are shared across all calls. 
- There are some edge cases with differing behaviour. Some are due to Scratch being a bit difficult to work with (e.g. handling of NaN, casting to bools). 
- There isn't a full guarantee that the code is perfectly formatted and valid in project.json. You may want to try some... let's call it *block laundering*. Load the project in the editor and save it again. 


### Future

- It would be great to add support for custom blocks with return statements.
- A form of templating or macro system to directly replace custom block calls could be implemented. These could be marked as such through name, say those starting with a particular keyword.
- The temporary variables extension should be investigated. It would be nice to support it but is probably very difficult to implement due to the many scenarios to consider.

