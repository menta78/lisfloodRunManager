function lfEvaEstimRetPerForYearMaxima(ncFlPath, varargin)

args.msrname = 'rl_min';
args.isLowExtremes = true; % if true, the signal has to be inverted before estimating the return period
args = easyParseNamedArgs(varargin, args);
msrname = args.msrname;
isLowExtremes = args.isLowExtremes;





