include "globals.mzn";



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
% Objective.
bool: ignore_sec_objective=false;
var int: sec_objective;
constraint sec_objective >= 0;  % trick to add a second part in the objective.
constraint (if ignore_sec_objective then
                sec_objective = 0
            else
                true
            endif);

%-----------------------------------------------------------------------------%
% Special constraint description
%-----------------------------------------------------------------------------%
% Start together penalty
int: nb_start_together;
array[1..nb_start_together] of Tasks: tasks_start_together_1;
array[1..nb_start_together] of Tasks: tasks_start_together_2;


% Start after lag penalty
int: nb_start_after_nunit;
array[1..nb_start_after_nunit] of Tasks: tasks_start_after_nunit_1;
array[1..nb_start_after_nunit] of Tasks: tasks_start_after_nunit_2;
array[1..nb_start_after_nunit] of int: lags_start_after_nunit;


% Start at end+offset penalty
int: nb_start_at_end_plus_offset;
array[1..nb_start_at_end_plus_offset] of Tasks: tasks_start_at_end_plus_offset_1;
array[1..nb_start_at_end_plus_offset] of Tasks: tasks_start_at_end_plus_offset_2;
array[1..nb_start_at_end_plus_offset] of int: lags_start_at_end_plus_offset;


% Start at end penalty
int: nb_start_at_end;
array[1..nb_start_at_end] of Tasks: tasks_start_at_end_1;
array[1..nb_start_at_end] of Tasks: tasks_start_at_end_2;


% start time window penalty
int: nb_start_window_low;
int: nb_start_window_up;
array[1..nb_start_window_low] of Tasks: task_id_low_start;
array[1..nb_start_window_up] of Tasks:  task_id_up_start;
array[1..nb_start_window_low] of 0..max_time: times_low_start;
array[1..nb_start_window_up] of 0..max_time: times_up_start;

% Hard Constraint
%constraint forall(i in 1..nb_start_window_low)(s[task_id_low_start[i]]>=times_low_start[i]);
%constraint forall(i in 1..nb_start_window_up)(s[task_id_up_start[i]]<=times_up_start[i]);
%
% Soft constraints (inspiration
%constraint sum(i in 1..nb_start_window_low)(max([times_low_start[i]-s[task_id_low_start[i]], 0]))==penalty_start_low;
%constraint sum(i in 1..nb_start_window_up)(max([-times_up_start[i]+s[task_id_up_start[i]], 0]))==penalty_start_up;


% end time window penalty
int: nb_end_window_low;
int: nb_end_window_up;
array[1..nb_end_window_low] of Tasks: task_id_low_end;
array[1..nb_end_window_up] of Tasks:  task_id_up_end;
array[1..nb_end_window_low] of 0..max_time: times_low_end;
array[1..nb_end_window_up] of 0..max_time: times_up_end;

%
%
%constraint sum(i in 1..nb_end_window_low)(max([times_low_end[i]-s[task_id_low_end[i]]+d[task_id_low_end[i]], 0]))==penalty_end_low;
%constraint sum(i in 1..nb_end_window_up)(max([-times_up_end[i]+s[task_id_up_end[i]]+d[task_id_up_end[i]], 0]))==penalty_end_up;




%-----------------------------------------------------------------------------%
% Model variables.

array [Tasks] of var Times: s;  % The start times
var 0..max_time: objective      ;  % The project duration (makespan)


% Put your constraints (reused from previous exercices for example)


%solve satisfy;
solve minimize objective+sec_objective;

%-----------------------------------------------------------------------------%
output ["Start times = ", show(s), "\n",
        "makespan = ", show(objective)];