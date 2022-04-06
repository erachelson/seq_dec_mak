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

------------------------------------%