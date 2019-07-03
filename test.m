%test environment
mdl = './some_simulink_model/rlCartPoleSimscapeModel';
open_system(mdl)
%Ts = 0.02;
%Tf = 25;
rng(0)
set_param('rlCartPoleSimscapeModel','SimulationCommand','start','SimulationCommand','pause');
set_param('rlCartPoleSimscapeModel', 'SimulationCommand', 'step'); 
%set_param(gcs,'SimulationCommand','start','SimulationCommand','pause');
