library(ncdf4)
library(pracma)

ncDisFlPath <- '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_dis_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc'
ncWlFlPath <- '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/projection_wl_rcp85_CLMcom-CCLM4-8-17_BC_MPI-M-MPI-ESM-LR_wuConst_statistics.nc'
ncIdChanFlPath <- '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/maps/idChan_5km.nc'
#ncDisFlPath <- '/ClimateRun4/multi-hazard/eva/projection_dis_rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_statistics.nc'
#ncWlFlPath <- '/ClimateRun4/multi-hazard/eva/projection_wl_rcp85_CLMcom-CCLM4-8-17_BC_ICHEC-EC-EARTH_wuConst_statistics.nc'
outNcFlPth <- '/STORAGE/src1/git/lisfloodRunManager/CORDEXRuns/lisfloodEVA/test/wl_dis_fit.nc'

ncIdChan <- nc_open(ncIdChanFlPath)
idChan_ <- t(ncvar_get(ncIdChan, 'idChan_5km.map'))
nc_close(ncIdChan)

ncDis <- nc_open(ncDisFlPath)
ncWl <- nc_open(ncWlFlPath)

x <- ncvar_get(ncDis, 'x')
y <- ncvar_get(ncDis, 'y')

#dis <- ncvar_get(ncDis, 'rl')
#wl <- ncvar_get(ncWl, 'rl')
dis_ymax <- ncvar_get(ncDis, 'year_max')
wl_ymax <- ncvar_get(ncWl, 'year_max')

nc_close(ncDis);
nc_close(ncWl);

nx <- dim(x)[1]
ny <- dim(y)[1]
sz = dim(dis)
dis_ <- array(data=dis, dim=c(ny, nx, sz[3]*sz[4]))
wl_ <- array(data=wl, dim=c(ny, nx, sz[3]*sz[4]))

chanCnd = !is.na(idChan_)
idChanUns = idChan_[chanCnd]
chanSortIndx = order(idChanUns)
idChan = idChanUns[chanSortIndx]
npt = length(idChan)

msxy = meshgrid(x, y)
xmtx = msxy$X
ymtx = msxy$Y
xChan = xmtx[chanCnd][chanSortIndx]
yChan = ymtx[chanCnd][chanSortIndx]

msixiy = meshgrid(1:nx, 1:ny)
ixmtx = msixiy$X;
iymtx = msixiy$Y;
ixpt = ixmtx[chanCnd][chanSortIndx]
iypt = iymtx[chanCnd][chanSortIndx]

# examples for 1 point
# ix <- 457
# iy <- 574
# 
# ix <- 454
# iy <- 592
# 
# ix <- 449
# iy <- 592
# 
# plot(dis_[iy, ix,], wl_[iy, ix,])
# mdl <- lm(log(wl_[iy, ix,]) ~ log(dis_[iy, ix,]))
# c = exp(mdl$coefficients[1])
# a = mdl$coefficients[2]
# plot(dis_[iy, ix,], wl_[iy, ix,])
# #par(new=T)
# lines(dis_[iy, ix,], c*dis_[iy, ix,]^a, col='red')

#amtx <- array(data=NaN, dim=c(ny, nx));
#cmtx <- array(data=NaN, dim=c(ny, nx));
aa <- array(data=NaN, dim=c(npt))
cc <- array(data=NaN, dim=c(npt))
xx <- array(data=NaN, dim=c(npt))
yy <- array(data=NaN, dim=c(npt))
# disflt <- array(data=NaN, dim=c(npt, dim(dis_)[3]))
# wlflt <- array(data=NaN, dim=c(npt, dim(dis_)[3]))
fitType <- array(data=0, dim=npt)

npathological = 0
for (ipt in 1:npt){
  if (mod(ipt, 100) == 0){
    print(paste0('  done % ', toString(ipt/npt*100)))
  }
  ix <- ixpt[ipt]
  iy <- iypt[ipt]
  ds <- dis_[iy, ix,]
  l <- wl_[iy, ix,]
  if (sum(is.na(ds)) > 0){
    next;
  }
  mdl <- lm(log(l) ~ log(ds))
  a <- mdl$coefficients[2]
  c <- exp(mdl$coefficients[1])
  if (a > 1){
    print(paste0('    a>1 for iy,ix=', toString(iy), ',', toString(ix), '. Fitting using the y maxima'))
    fitType[ipt] = 1;
    
    ds <- dis_ymax[iy, ix,]
    l <- wl_ymax[iy, ix,]
    mdl <- lm(log(l) ~ log(ds))
    a <- mdl$coefficients[2]
    c <- exp(mdl$coefficients[1])
    
    if (a > 1){
      fitType[ipt] = 2;
      print(paste0('        still a>1 for iy,ix=', toString(iy), ',', toString(ix), '. Using linear fit'))
      mdl <- lm(l ~ 0 + ds)
      a <- 1
      c <- mdl$coefficients[1]
      npathological = npathological+1
    }
  }
  aa[ipt] <- a
  cc[ipt] <- c
  xx[ipt] <- x[ix]
  yy[ipt] <- y[iy]
  
#   disflt[ipt,] <- ds
#   wlflt[ipt,] <- l
}

print(paste0('% of pathological point: ', toString(npathological/ipt*100)))

# xdim <- ncdim_def("x", "", x)
# ydim <- ncdim_def("y", "", y)
# a_def <- ncvar_def("a", "", list(ydim, xdim))
# c_def <- ncvar_def("c", "", list(ydim, xdim))
# ncout = nc_create(outNcFlPth, list(a_def, c_def), force_v4=T)
# ncvar_put(ncout, a_def, amtx)
# ncvar_put(ncout, c_def, cmtx)
# nc_close(ncout)

ptdim <- ncdim_def("pt", "", idChan, longname="pt id")
a_def <- ncvar_def("a", "", list(ptdim), longname="exponent, wl = c*dis^a")
c_def <- ncvar_def("c", "", list(ptdim), longname="factor, wl = c*dis^a")
fitTyp_def <- ncvar_def("fit_type", "", list(ptdim), longname="type of fit")
x_def <- ncvar_def("x", "", list(ptdim), longname="x")
y_def <- ncvar_def("y", "", list(ptdim), longname="y")
ncout = nc_create(outNcFlPth, list(a_def, c_def, fitTyp_def, x_def, y_def), force_v4=T)
ncvar_put(ncout, a_def, aa)
ncvar_put(ncout, c_def, cc)
ncvar_put(ncout, x_def, xx)
ncvar_put(ncout, y_def, yy)
ncvar_put(ncout, fitTyp_def, fitType)
ncatt_put(ncout, "fit_type", "description", "0 if power law of return levels, 1 if power law of yearly maxima, 2 if linear fit of yearly maxima.")
nc_close(ncout)

# test
nctst = nc_open(outNcFlPth)
xout = ncvar_get(nctst, 'x')
yout = ncvar_get(nctst, 'y')
aout = ncvar_get(nctst, 'a')
cout = ncvar_get(nctst, 'c')
ft = ncvar_get(nctst, 'fit_type')
nc_close(nctst);

xy = data.frame(x=xout, y=yout, a=aout, c=cout, ft=ft);
pa = ggplot(xy, aes(x=x, y=y, color=a)) + geom_point(size=.1);
pc = ggplot(xy, aes(x=x, y=y, color=c)) + geom_point(size=.1);
pft = ggplot(xy, aes(x=x, y=y, color=ft)) + geom_point(size=.1);

# checking some points with linear fit
ilin = which(ft == 2)
ipt = ilin[50]
ix_ = ixpt[ipt]
iy_ = iypt[ipt]
ds_ = dis_ymax[iy_, ix_,]; 
ai = aout[ipt]
ci = cout[ipt]
plot(ds_, wl_ymax[iy_, ix_,])
lines(ds_, ci*ds_^ai)
# plot(ds_, ci*ds_^ai)


