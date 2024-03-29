%include "rcpsp.mzn";

%-----------------------------------------------------------------------------%
% vim: ts=4 sw=4 et wm=0 tw=0
%-----------------------------------------------------------------------------%
% Copyright (C) 2009-2012 The University of Melbourne and NICTA.
% See the file COPYING for license information.
%-----------------------------------------------------------------------------%
% Model example for Resource-Constrained Project Scheduling Problems (RCPSP)
%
% A RCPSP consists of resources, tasks, and precedences between some tasks
% where resources have of a specific capacity and tasks need some capacity of
% some resource to be executed.
% Here, we consider resources with a constant discrete capacity over time and
% tasks with a constant discrete duration and resource requirements.
% The objective is to find a optimal schedule with respect to the earliest end
% time of the schedule where the tasks' resource requirements do not exceed
% the resource capacities to any time and each precedence is met.
%
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


% Fake Tasks (to handle notably the varying resource availability)
%bool: include_fake_tasks;
%int: max_duration_fake_task;
%int: n_fake_tasks;
%set of int: FakeAct=1..n_fake_tasks;
%array[FakeAct] of 0..max_time: fakestart;
%array[FakeAct] of 1..max_duration_fake_task: fakedur;
%array[Res,FakeAct] of 0..max(rc): fakereq;

% Planning horizon
% int: t_max = sum(i in Tasks)(d[i]);     % End time of the planning horizon
% set of int: Times = 0..t_max-1;     % Possible start times
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
                 %if include_fake_tasks  then
                 %   let{set of FakeAct: FTasks = {j | j in FakeAct where fakereq[r, j]>0}}
                 %     in(
                 %       cumulative([ s[i] | i in RTasks ]++[fakestart[p] | p in FTasks],
                 %                  [ d[i] | i in RTasks ]++[fakedur[p] | p in FTasks],
                 %                  [ rr[r, i] | i in RTasks ]++[fakereq[r, p] | p in FTasks],
                 %                  rc[r])
                 %       )
                 if sum_rr > rc[r] then
                        cumulative([ s[i] | i in RTasks ],
                                   [ d[i] | i in RTasks ],
                                   [ rr[r, i] | i in RTasks ],
                                   rc[r])
                  else
                        true
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
constraint sec_objective>=0;
constraint (if ignore_sec_objective then
                sec_objective = 0
            else
                true
            endif);



% TODO...
%-----------------------------------------------------------------------------%
% Special constraint description
%-----------------------------------------------------------------------------%
% Start together penalty
int: nb_start_together;
array[1..nb_start_together] of Tasks: tasks_start_together_1;
array[1..nb_start_together] of Tasks: tasks_start_together_2;
constraint forall(i in 1..nb_start_together)(s[tasks_start_together_1[i]]==s[tasks_start_together_2[i]]);


% Start after lag penalty
int: nb_start_after_nunit;
array[1..nb_start_after_nunit] of Tasks: tasks_start_after_nunit_1;
array[1..nb_start_after_nunit] of Tasks: tasks_start_after_nunit_2;
array[1..nb_start_after_nunit] of int: lags_start_after_nunit;
constraint forall(i in 1..nb_start_after_nunit)(s[tasks_start_after_nunit_2[i]]>=
                                                s[tasks_start_after_nunit_1[i]]+lags_start_after_nunit[i]);


% Start at end+offset penalty
int: nb_start_at_end_plus_offset;
array[1..nb_start_at_end_plus_offset] of Tasks: tasks_start_at_end_plus_offset_1;
array[1..nb_start_at_end_plus_offset] of Tasks: tasks_start_at_end_plus_offset_2;
array[1..nb_start_at_end_plus_offset] of int: lags_start_at_end_plus_offset;
constraint forall(i in 1..nb_start_at_end_plus_offset)(s[tasks_start_at_end_plus_offset_2[i]]>=
                                                       s[tasks_start_at_end_plus_offset_1[i]]
                                                       +d[tasks_start_at_end_plus_offset_1[i]]
                                                       +lags_start_at_end_plus_offset[i]);


% Start at end penalty
int: nb_start_at_end;
array[1..nb_start_at_end] of Tasks: tasks_start_at_end_1;
array[1..nb_start_at_end] of Tasks: tasks_start_at_end_2;
constraint forall(i in 1..nb_start_at_end)(s[tasks_start_at_end_2[i]]==s[tasks_start_at_end_1[i]]+
                                           d[tasks_start_at_end_1[i]]);




% start time window penalty
int: nb_start_window_low;
int: nb_start_window_up;
array[1..nb_start_window_low] of Tasks: task_id_low_start;
array[1..nb_start_window_up] of Tasks:  task_id_up_start;
array[1..nb_start_window_low] of 0..max_time: times_low_start;
array[1..nb_start_window_up] of 0..max_time: times_up_start;

% Hard Constraint
constraint forall(i in 1..nb_start_window_low)(s[task_id_low_start[i]]>=times_low_start[i]);
constraint forall(i in 1..nb_start_window_up)(s[task_id_up_start[i]]<=times_up_start[i]);
%


% end time window penalty
int: nb_end_window_low;
int: nb_end_window_up;
array[1..nb_end_window_low] of Tasks: task_id_low_end;
array[1..nb_end_window_up] of Tasks:  task_id_up_end;
array[1..nb_end_window_low] of 0..max_time: times_low_end;
array[1..nb_end_window_up] of 0..max_time: times_up_end;

constraint forall(i in 1..nb_end_window_low)(s[task_id_low_end[i]]+d[task_id_low_end[i]]>=times_low_end[i]);
constraint forall(i in 1..nb_end_window_up)(s[task_id_up_end[i]]+d[task_id_up_end[i]]<=times_up_end[i]);



%solve satisfy;
solve
   :: int_search( s ++ [objective], input_order, indomain_min) %, complete )
   %:: int_search( s ++ [objective], smallest, indomain_min, complete) %, complete )
   minimize objective+sec_objective;

%-----------------------------------------------------------------------------%
output [
    "Start times = ", show(s), "\n",
    "makespan = ", show(objective), "\n",
    "sec objective = ", show(sec_objective), "\n",
    "rr=", show(rr)];