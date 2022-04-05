include "cumulative.mzn";
int: max_time;
set of int: TIMES=0..max_time;
int: n_res;                     % The number of resources
set of int: Res = 1..n_res;     % The set of all resources
array [Res] of int: rc;         % The resource capabilities


% Tasks
%
int: n_tasks;                           % The number of tasks
set of int: Tasks = 1..n_tasks;         % The set of all tasks
array [Tasks] of int: d;                % The task durations
array [Res, Tasks] of int: rr ;         % The resource requirements
array [Tasks, Tasks] of bool: suc;      % Adjacency matrix
array [Tasks] of set of Tasks: successors = [{p|p in Tasks where suc[j,p]}|j in Tasks];

% Variable
array [Tasks] of var TIMES: start;  % The start times
var TIMES: makespan      ;  % The project duration (makespan)

% precedence constraints :
constraint forall(t in Tasks)(forall(tt in successors[t])(start[tt]>=start[t]+d[t]));

% cumulative constraints :
bool: simplify_cumulative = true;
constraint forall(r in Res)(cumulative(start, d, row(rr, r), rc[r]));

constraint forall(r in Res)
                (if simplify_cumulative then
                    let{set of Tasks: subtasks={t| t in Tasks where rr[r, t]>0}} in
                    (
                        cumulative([start[sub]|sub in subtasks],
                                   [d[sub]| sub in subtasks],
                                   [rr[r, sub]| sub in subtasks],
                                   rc[r])
                     )
                endif);
constraint forall(t in Tasks)(makespan>=start[t]+d[t]);
solve minimize makespan;
% WRITE YOUR CONSTRAINTS :) !!!
output ["makespan = \(makespan)"];

