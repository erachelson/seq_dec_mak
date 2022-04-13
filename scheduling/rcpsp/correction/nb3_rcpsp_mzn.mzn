%-----------------------------------------------------------------------------%

include "cumulative.mzn";

%-----------------------------------------------------------------------------%
% Model parameters.


% Resources
%
int: n_res;                     % The number of resources
set of int: Res = 1..n_res;     % The set of all resources
array [Res] of int: rc;         % The resource capabilities

% Tasks
%
int: n_tasks;                           % The number of tasks
set of int: Tasks = 1..n_tasks;         % The set of all tasks
array [Tasks]      of int       : d  ;  % The task durations
array [Res, Tasks] of int       : rr ;  % The resource requirements
array [Tasks, Tasks] of bool: adj;
array [Tasks]      of set of int: suc=[{p|p in Tasks where adj[j,p]}|j in Tasks];


% Planning horizon
int: max_time;
set of int: Times = 0..max_time;     % Possible start times


%-----------------------------------------------------------------------------%
% Model variables.

array [Tasks] of var Times: s;  % The start times
var 0..max_time: objective      ;  % The project duration (makespan)

%-----------------------------------------------------------------------------%
% Constraints.

    % Precedence constraints
    %
constraint
   forall ( i in Tasks, j in suc[i] )
   (
         s[i] + d[i] <= s[j]
   );

    % Redundant non-overlapping constraints
    %
constraint
    forall ( i, j in Tasks where i < j )
    (
        if exists(r in Res)(rr[r, i] + rr[r, j] > rc[r]) then
            s[i] + d[i] <= s[j]   \/ s[j] + d[j] <= s[i]
        else
            true
        endif
    );


constraint forall(r in Res)(
               forall(i in Tasks)(
                    if d[i]>0 then
                      assert(rr[r, i]<=rc[r], "Task \(i) consuming more resource \(r) than available")
                      %rr[r,i]<=rc[r]
                    else
                        true
                    endif
           ));


% Cumulative resource constraints
%
constraint
     forall ( r in Res )
     (
         let {
             set of int: RTasks =
                             { i | i in Tasks
                             where rr[r, i] > 0 /\ d[i] > 0 },
             int: sum_rr = sum(i in RTasks)(rr[r, i])
         } in (
             if RTasks != {} then
                if sum_rr > rc[r] then
                        cumulative([ s[i] | i in RTasks ],
                                   [ d[i] | i in RTasks ],
                                   [ rr[r, i] | i in RTasks ],
                                   rc[r])

                 endif
             endif
         )
     );

% Makespan constraints
bool: add_objective_makespan=true; % by default True. but by setting it false you can modify your objective function outside (i.e minizinc pyyhon)
constraint(if add_objective_makespan then
               forall ( i in Tasks where suc[i] == {} )
               (
                  s[i] + d[i] <= objective
               )
           else
                true
           endif);

%-----------------------------------------------------------------------------%
% Objective.
bool: ignore_sec_objective=true;
var int: sec_objective;
constraint sec_objective>=0; % trick to add a second part in the objective.
constraint (if ignore_sec_objective then
                sec_objective = 0
            else
                true
            endif);



%solve satisfy;
solve
   :: int_search( s ++ [objective], smallest, indomain_min) %, complete )
   %:: int_search( s ++ [objective], smallest, indomain_min, complete) %, complete )
   minimize objective+sec_objective;

%-----------------------------------------------------------------------------%
output [
    "Start times = ", show(s), "\n",
    "makespan = ", show(objective), "\n",
    "sec objective = ", show(sec_objective), "\n",
    "rr=", show(rr)];

%-----------------------------------------------------------------------------%
%-----------------------------------------------------------------------------%