% Input
int: x=2;
int: y=2;

% Decision variable
var int: z;
% Addition constraint
constraint z=x+y;

% Solve command
solve satisfy;

% Output
output ["z=x+y : \(z)=\(x)+\(y)"];