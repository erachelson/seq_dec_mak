% Colouring Australia using nc colors 
int: nc=4; 
set of int: range_color=1..nc;

% Variable color for each region.
var range_color: wa;    
var range_color: nt;     
var range_color: sa;    
var range_color: q;     
var range_color: nsw;   
var range_color: v;
var range_color: t;

constraint wa != nt;
constraint wa != sa;
constraint nt != sa;
constraint nt != q;
constraint sa != q;
constraint sa != nsw;
constraint sa != v;
constraint q != nsw;
constraint nsw != v;

solve satisfy;