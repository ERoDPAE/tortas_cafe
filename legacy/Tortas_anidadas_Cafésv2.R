library(readr)
library(reshape2)
library(dplyr)

setwd("//arba-30m/GRP/IT/Shared/XFXP15/11. Café/Datos_torta_anidada/")
temp = list.files(pattern="*.csv")
for (i in 1:length(temp)) assign(temp[i], read.csv(temp[i]))

#put all data frames into list
df_list <- list(export_1.csv, export_2.csv, export_3.csv,export_4.csv,
                export_5.csv,export_6.csv,export_7.csv,export_8.csv,export_9.csv,export_10.csv,
                export_11.csv,export_12.csv,export_13.csv,export_14.csv,export_15.csv,export_16.csv,export_17.csv)

#merge all data frames in list
base_agrupada <- Reduce(function(x, y) merge(x, y,by=c("estacion","hora"),all=TRUE), df_list)

base_agrupada[-1] <- sapply(base_agrupada[-1],as.numeric)
base_agrupada[is.na(base_agrupada)] <- 0

base_agrupada$q_cafes_llevar_algo_leche_sinbakery <- base_agrupada$q_cafes_llevar_algo_leche_sinbakery - base_agrupada$q_cafes_llevar_solo_leche
base_agrupada$q_cafes_local_algo_leche_sinbakery <- base_agrupada$q_cafes_local_algo_leche_sinbakery - base_agrupada$q_cafes_local_solo_leche
base_agrupada$q_cafes_llevar_algo_otros_sinbakery <- base_agrupada$q_cafes_llevar_algo_otros_sinbakery - base_agrupada$q_cafes_llevar_solo_otros
base_agrupada$q_cafes_local_algo_otros_sinbakery <- base_agrupada$q_cafes_local_algo_otros_sinbakery - base_agrupada$q_cafes_local_solo_otros

base_agrupada$q_cafes_llevar_algo_leche_sinbakery_sinsandwich_sin_caramelo <- base_agrupada$q_cafes_llevar_algo_leche_sinbakery - base_agrupada$q_cafes_llevar_algo_leche_sinbakery_sandwiches - base_agrupada$q_cafes_llevar_algo_leche_sinbakery_sinsandwiches_caramelos
base_agrupada$q_cafes_local_algo_leche_sinbakery_sinsandwich_sin_caramelo <-  base_agrupada$q_cafes_local_algo_leche_sinbakery - base_agrupada$q_cafes_local_algo_leche_sinbakery_sandwiches - base_agrupada$q_cafes_local_algo_leche_sinbakery_sinsandwiches_caramelos
base_agrupada$q_cafes_llevar_algo_otros_sinbakery_sinsandwich_sin_caramelo <- base_agrupada$q_cafes_llevar_algo_otros_sinbakery - base_agrupada$q_cafes_llevar_algo_otros_sinbakery_sandwiches - base_agrupada$q_cafes_llevar_algo_otros_sinbakery_sinsandwiches_caramelos
base_agrupada$q_cafes_local_algo_otros_sinbakery_sinsandwich_sin_caramelo <-  base_agrupada$q_cafes_local_algo_otros_sinbakery - base_agrupada$q_cafes_local_algo_otros_sinbakery_sandwiches - base_agrupada$q_cafes_local_algo_otros_sinbakery_sinsandwiches_caramelos
base_agrupada$q_cafes_local_1 <- base_agrupada$q_cafes_local - base_agrupada$q_cafes_local_mas_1
base_agrupada$q_cafes_llevar_1 <- base_agrupada$q_cafes_llevar - base_agrupada$q_cafes_llevar_mas_1

base_agrupada$q_cafes_llevar_solo_otros_nonegro <- base_agrupada$q_cafes_llevar_solo_otros - base_agrupada$q_cafes_llevar_solo_otros_negro1
base_agrupada$q_cafes_local_solo_otros_nonegro <- base_agrupada$q_cafes_local_solo_otros - base_agrupada$q_cafes_local_solo_otros_negro1

base_agrupada$q_cafes_llevar_algo_otros_nonegro <- base_agrupada$q_cafes_llevar_algo_otros - base_agrupada$q_cafes_llevar_algo_otros_negro1
base_agrupada$q_cafes_local_algo_otros_nonegro <- base_agrupada$q_cafes_local_algo_otros - base_agrupada$q_cafes_local_algo_otros_negro1


base_agrupada$q_cafes_local_algo_otros_sinbakery_nonegro <- base_agrupada$q_cafes_local_algo_otros_sinbakery - base_agrupada$q_cafes_local_algo_otros_sinbakery_negro
base_agrupada$q_cafes_llevar_algo_otros_sinbakery_nonegro <- base_agrupada$q_cafes_llevar_algo_otros_sinbakery - base_agrupada$q_cafes_llevar_algo_otros_sinbakery_negro


base_agrupada$q_cafes_llevar_algo_otros_bakery_nonegro <-base_agrupada$q_cafes_llevar_algo_otros_bakery - base_agrupada$q_cafes_llevar_algo_bakery_negro1
base_agrupada$q_cafes_local_algo_otros_bakery_nonegro <-base_agrupada$q_cafes_local_algo_otros_bakery - base_agrupada$q_cafes_local_algo_bakery_negro1


base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_sincaramelos <- base_agrupada$q_cafes_local_algo_otros_sinbakery_negro - base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_choco - base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_caramelonochoco

base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_caramelos_total <- base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_choco + base_agrupada$q_cafes_local_algo_otros_sinbakery_negro_caramelonochoco


# library(writexl)
# base_long <- base_agrupada %>% group_by(estacion) %>% summarise(across(-hora, sum))
# write_xlsx(x = base_long,path = "//arba-30m/GRP/IT/Shared/XFXP15/11. Café/datos_long3.xlsx")


# base_agrupada$q_cafes_llevar_algo_leche_sinbakery_sinalfajor <- base_agrupada$q_cafes_llevar_algo_leche_sinbakery - base_agrupada$q_cafes_llevar_algo_leche_sinbakery_alfajor
# base_agrupada$q_cafes_local_algo_leche_sinbakery_sinalfajor <-  base_agrupada$q_cafes_local_algo_leche_sinbakery - base_agrupada$q_cafes_local_algo_leche_sinbakery_alfajor
# base_agrupada$q_cafes_llevar_algo_otros_sinbakery_sinalfajor <- base_agrupada$q_cafes_llevar_algo_otros_sinbakery - base_agrupada$q_cafes_llevar_algo_otros_sinbakery_alfajor
# base_agrupada$q_cafes_local_algo_otros_sinbakery_sinalfajor <-  base_agrupada$q_cafes_local_algo_otros_sinbakery - base_agrupada$q_cafes_local_algo_otros_sinbakery_alfajor
# 
# base_agrupada$q_cafes_llevar_algo_leche_sinbakery_alfajor_sincachafaz <- base_agrupada$q_cafes_llevar_algo_leche_sinbakery_alfajor - base_agrupada$q_cafes_llevar_algo_leche_sinbakery_alfajor_cachafaz
# base_agrupada$q_cafes_local_algo_leche_sinbakery_alfajor_sincachafaz <-  base_agrupada$q_cafes_local_algo_leche_sinbakery_alfajor - base_agrupada$q_cafes_local_algo_leche_sinbakery_alfajor_cachafaz
# base_agrupada$q_cafes_llevar_algo_otros_sinbakery_alfajor_sincachafaz <- base_agrupada$q_cafes_llevar_algo_otros_sinbakery_alfajor - base_agrupada$q_cafes_llevar_algo_otros_sinbakery_alfajor_cachafaz
# base_agrupada$q_cafes_local_algo_otros_sinbakery_alfajor_sincachafaz <-  base_agrupada$q_cafes_local_algo_otros_sinbakery_alfajor - base_agrupada$q_cafes_local_algo_otros_sinbakery_alfajor_cachafaz



base_agrupada <- melt(base_agrupada,id.vars=c("estacion","hora"))
base_agrupada <-base_agrupada[base_agrupada$estacion!="CORS EVENTOS",]


base_agrupada$Nivel1 <- case_when(grepl("llevar", base_agrupada$variable)~"LLevar",
                                  grepl("local", base_agrupada$variable)~"Local",
                                  TRUE~"NA")
base_agrupada$Nivel2 <- case_when(grepl("algo", base_agrupada$variable)~"Algo",
                                  grepl("solo", base_agrupada$variable)~"Solo",
                                  TRUE~"NA")
base_agrupada$Nivel2 <- paste(base_agrupada$Nivel1,base_agrupada$Nivel2,sep=" - ")

base_agrupada$Nivel2b <- case_when(grepl("mas_1", base_agrupada$variable)~"> 1 ud",
                                   grepl("llevar_1", base_agrupada$variable)~"1 ud",
                                   grepl("local_1", base_agrupada$variable)~"1 ud",
                                   TRUE~"NA")
base_agrupada$Nivel2b <- paste(base_agrupada$Nivel1,base_agrupada$Nivel2b,sep=" - ")

base_agrupada$Nivel3 <- case_when(grepl("leche", base_agrupada$variable)~"Leche",
                                  grepl("otros", base_agrupada$variable)~"Otros",
                                  TRUE~"NA")

base_agrupada$Nivel3 <- paste(base_agrupada$Nivel2,base_agrupada$Nivel3,sep=" - ")

base_agrupada$Nivel4 <- case_when(grepl("_sinbakery", base_agrupada$variable)~"Sin_Bakery",
                                  grepl("_bakery", base_agrupada$variable)~"Bakery",
                                  grepl("negro1", base_agrupada$variable)~"Negro",
                                  TRUE~"NA")

base_agrupada$Nivel4 <- paste(base_agrupada$Nivel3,base_agrupada$Nivel4,sep=" - ")


base_agrupada$Nivel5 <- case_when(grepl("sinsandwiches_caramelos", base_agrupada$variable)~"Caramelo",
                                  grepl("_sinsandwich", base_agrupada$variable)~"Sin_Sandwich",
                                  grepl("_sandwiches", base_agrupada$variable)~"Sandwich",
                                  
                                  TRUE~"NA")

base_agrupada$Nivel5 <- paste(base_agrupada$Nivel4,base_agrupada$Nivel5,sep=" - ")


library(readxl)
df_cluster_resultados_finales <- read_excel("//arba-30m/GRP/IT/Shared/XFXP15/11. Café/Datos_torta_anidada/df_cluster_resultados_finales.xlsx")
df_cluster_resultados_finales <- df_cluster_resultados_finales %>% select(`PBL Name`,Cluster_combinado) %>% mutate(`PBL Name`=toupper(`PBL Name`) )
base_agrupada$estacion <- toupper(base_agrupada$estacion)
base_agrupada <- merge(base_agrupada,df_cluster_resultados_finales,by.x="estacion",by.y="PBL Name",all.x=T)
unique(base_agrupada$estacion[is.na(base_agrupada$Cluster_combinado)])

base_agrupada <-base_agrupada[! base_agrupada$estacion %in% c("DISC CARAFFA","DISC ECHEVERRIA","DISC PANAMERICANA"),]

base_agrupada$agrupacion_1 <- case_when(grepl(" - Bakery",base_agrupada$Nivel4)~"Bakery",
                                        grepl("Sin_Bakery",base_agrupada$Nivel4)~"Sin Bakery",
                                        grepl("Solo",base_agrupada$Nivel4)~"Solo",
                                        TRUE~"NA")
base_agrupada$agrupacion_2 <- case_when(grepl("_negro",base_agrupada$variable)~"Negro",
                                        grepl("_nonegro",base_agrupada$variable)~"No Negro",
                                        grepl("_leche",base_agrupada$variable)~"Leche",
                                        TRUE~"NA")
base_agrupada$agrupacion_3 <- case_when(grepl("_caramelonochoco",base_agrupada$variable)~"Caramelo",
                                        grepl("_choco",base_agrupada$variable)~"Chocolate",
                                        TRUE~"Otros")

unique(base_agrupada$variable)

#EXTRAS----------------------------------------------
porc_2_o_mas <- base_agrupada %>%
  dplyr::filter(variable %in% c("q_cafes_local_mas_1","q_cafes_local_1")) %>% 
  dplyr::group_by(estacion) %>% 
  dplyr::mutate(Cantidad_est=sum(value,na.rm=T)) %>% ungroup() %>% 
  dplyr::group_by(estacion,variable) %>% 
  dplyr::summarise(porcentaje_abs=sum(value,na.rm=T)/max(Cantidad_est))

# library(esquisse)
# esquisse::esquisser()

library(ggplot2)
porc_2_o_mas %>%
  filter(variable %in% "q_cafes_local_mas_1") %>%
  ggplot() +
  aes(x = reorder(estacion,porcentaje_abs), weight = porcentaje_abs) +
  geom_bar(fill = "#112446") +theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust=1)) 


prueba <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_algo_leche","q_cafes_local_algo_leche",
                                                              "q_cafes_llevar_algo_otros_nonegro","q_cafes_local_algo_otros_nonegro",
                                                              "q_cafes_llevar_algo_otros_negro1","q_cafes_local_algo_otros_negro1",
                                                              "q_cafes_llevar_solo_otros_nonegro","q_cafes_local_solo_otros_nonegro",
                                                              "q_cafes_llevar_solo_otros_negro1","q_cafes_local_solo_otros_negro1",
                                                              "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(Nivel3) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(Nivel4,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))

sum(prueba$Cantidad_segmento)





prueba2 <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_local_algo_leche_bakery",
                                                              "q_cafes_local_algo_otros_bakery",
                                                              "q_cafes_local_algo_leche_sinbakery",
                                                              "q_cafes_local_algo_otros_sinbakery_nonegro",
                                                              "q_cafes_local_algo_otros_sinbakery_negro",
                                                              "q_cafes_local_solo_otros_nonegro",
                                                              "q_cafes_local_solo_otros_negro1",
                                                              "q_cafes_local_solo_leche")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(agrupacion_1) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(agrupacion_1,agrupacion_2,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))

sum(prueba2$Cantidad_segmento)

# Subcategorias_cafes_negros_sin_bakery <- read_csv("//arba-30m/GRP/IT/Shared/XFXP15/11. Café/Subcategorias_cafes_negros_sin_bakery.csv")
# 
# Subcategorias_cafes_negros_sin_bakery_agrupado <- Subcategorias_cafes_negros_sin_bakery %>% dplyr::group_by(categoria) %>% 
#   dplyr::summarise(q=sum(q_producto))

#TORTAS ANIDADAS-------------------------------------
library(plyr)
library(plotrix)
library(readxl)
library(tiff)
library(ggplot2)

tortas <- function(base_agrupada,Titulo){
interior <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_llevar","q_cafes_local")) %>% 
  dplyr::group_by(Nivel1) %>% 
  dplyr::summarise(Cantidad=sum(value,na.rm=T)) %>% 
  mutate(porcentaje_abs=Cantidad/sum(Cantidad,na.rm=T))

if(sum(interior$Cantidad)<3500){
  
}else{
exterior <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo","q_cafes_local_solo",
                                                              "q_cafes_llevar_algo","q_cafes_local_algo")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(Nivel1) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(Nivel2,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
sum(exterior$Cantidad_segmento)


exterior_2 <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
                                                              "q_cafes_llevar_algo_leche","q_cafes_local_algo_leche",
                                                              "q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
                                                              "q_cafes_llevar_algo_otros","q_cafes_local_algo_otros")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(Nivel2) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(Nivel3,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
sum(exterior_2$Cantidad_segmento)


exterior_3 <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
                                                              "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
                                                              "q_cafes_llevar_algo_leche_sinbakery","q_cafes_local_algo_leche_sinbakery",
                                                              "q_cafes_llevar_algo_otros_sinbakery","q_cafes_local_algo_otros_sinbakery",
                                                              "q_cafes_llevar_solo_otros_nonegro","q_cafes_local_solo_otros_nonegro",
                                                              "q_cafes_llevar_solo_otros_negro1","q_cafes_local_solo_otros_negro1",
                                                              "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(Nivel3) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(Nivel4,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))

sum(exterior_3$Cantidad_segmento)



exterior_4 <- base_agrupada %>%
  dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
                                                              "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
                                                              "q_cafes_llevar_solo_leche_bakery","q_cafes_local_solo_leche_bakery",
                                                              "q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
                                                              "q_cafes_llevar_solo_otros_bakery","q_cafes_local_solo_otros_bakery",
                                                              "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
                                                              "q_cafes_llevar_solo_leche_sinbakery","q_cafes_local_solo_leche_sinbakery",
                                                              "q_cafes_llevar_solo_otros_sinbakery","q_cafes_local_solo_otros_sinbakery",
                                                              "q_cafes_llevar_algo_leche_sinbakery_sinsandwich_sin_caramelo","q_cafes_local_algo_leche_sinbakery_sinsandwich_sin_caramelo",
                                                              "q_cafes_llevar_algo_otros_sinbakery_sinsandwich_sin_caramelo","q_cafes_local_algo_otros_sinbakery_sinsandwich_sin_caramelo",
                                                              "q_cafes_llevar_algo_leche_sinbakery_sinsandwiches_caramelos","q_cafes_local_algo_leche_sinbakery_sinsandwiches_caramelos",
                                                              "q_cafes_llevar_algo_otros_sinbakery_sinsandwiches_caramelos","q_cafes_local_algo_otros_sinbakery_sinsandwiches_caramelos",
                                                              "q_cafes_llevar_algo_leche_sinbakery_sandwiches","q_cafes_local_algo_leche_sinbakery_sandwiches",
                                                               "q_cafes_llevar_algo_otros_sinbakery_sandwiches","q_cafes_local_algo_otros_sinbakery_sandwiches")) %>% 
  dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
  dplyr::group_by(Nivel4) %>%
  dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
  ungroup() %>% 
  dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
  dplyr::group_by(Nivel5,variable) %>% 
  dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))

sum(exterior_4$Cantidad_segmento)

exterior_2 <- exterior_2[exterior_2$porcentaje_abs>0,]
exterior_3 <- exterior_3[exterior_3$porcentaje_abs>0,]
exterior_4 <- exterior_4[exterior_4$porcentaje_abs>0,]
# 
# exterior_5 <- base_agrupada %>%
#   dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
#                                                               "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
#                                                               "q_cafes_llevar_solo_leche_bakery","q_cafes_local_solo_leche_bakery",
#                                                               "q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
#                                                               "q_cafes_llevar_solo_otros_bakery","q_cafes_local_solo_otros_bakery",
#                                                               "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
#                                                               "q_cafes_llevar_solo_leche_sinbakery","q_cafes_local_solo_leche_sinbakery",
#                                                               "q_cafes_llevar_solo_otros_sinbakery","q_cafes_local_solo_otros_sinbakery",
#                                                               "q_cafes_llevar_algo_leche_sinbakery_sinalfajor","q_cafes_local_algo_leche_sinbakery_sinalfajor",
#                                                               "q_cafes_llevar_algo_otros_sinbakery_sinalfajor","q_cafes_local_algo_otros_sinbakery_sinalfajor",
#                                                               "q_cafes_llevar_algo_leche_sinbakery_alfajor_cachafaz","q_cafes_local_algo_leche_sinbakery_alfajor_cachafaz",
#                                                               "q_cafes_llevar_algo_otros_sinbakery_alfajor_cachafaz","q_cafes_local_algo_otros_sinbakery_alfajor_cachafaz",
#                                                               "q_cafes_llevar_algo_leche_sinbakery_alfajor_sincachafaz","q_cafes_local_algo_leche_sinbakery_alfajor_sincachafaz",
#                                                               "q_cafes_llevar_algo_otros_sinbakery_alfajor_sincachafaz","q_cafes_local_algo_otros_sinbakery_alfajor_sincachafaz")) %>% 
#   dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
#   dplyr::group_by(Nivel5) %>%
#   dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
#   ungroup() %>% 
#   dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
#   dplyr::group_by(Nivel6,variable) %>% 
#   dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
# 
# sum(exterior_5$Cantidad_segmento)

porcent_abs_externo <- exterior$porcentaje_abs
porcent_abs_externo_2 <- exterior_2$porcentaje_abs
porcent_abs_externo_3 <- exterior_3$porcentaje_abs
porcent_abs_externo_4 <- exterior_4$porcentaje_abs
# porcent_abs_externo_5 <- exterior_5$porcentaje_abs

tabla <- table(exterior$Nivel2)[order(unique(exterior$Nivel2))]
tabla_2 <- table(exterior_2$Nivel3)[order(unique(exterior_2$Nivel3))]
tabla_3 <- table(exterior_3$Nivel4)[order(unique(exterior_3$Nivel4))]
tabla_4 <- table(exterior_4$Nivel5)[order(unique(exterior_4$Nivel5))]
# tabla_5 <- table(exterior_5$Nivel6)[order(unique(exterior_5$Nivel6))]


#Armado grafico
colores=c("#EC8080","#D52220")
col_int <- rep_len(colores,length(interior$Nivel1))
col_ext <- lapply(Map(rep,colores[seq_along(tabla)],tabla),
                  function(porcent_abs_externo){
                    al <- head(seq(0,1,length.out=length(porcent_abs_externo)+2L)[-1L],-1L)
                    Vectorize(adjustcolor)(porcent_abs_externo,alpha.f=al)})

col_ext_2 <- lapply(Map(rep,colores[seq_along(tabla_2)],tabla_2),
                    function(porcent_abs_externo_2){
                      al <- head(seq(0,1,length.out=length(porcent_abs_externo_2)+2L)[-1L],-1L)
                      Vectorize(adjustcolor)(porcent_abs_externo_2,alpha.f=al)})

col_ext_3 <- lapply(Map(rep,colores[seq_along(tabla_3)],tabla_3),
                    function(porcent_abs_externo_3){
                      al <- head(seq(0,1,length.out=length(porcent_abs_externo_3)+2L)[-1L],-1L)
                      Vectorize(adjustcolor)(porcent_abs_externo_3,alpha.f=al)})

# col_ext_4 <- lapply(Map(rep,colores[seq_along(tabla_4)],tabla_4),
#                     function(porcent_abs_externo_4){
#                       al <- head(seq(0,1,length.out=length(porcent_abs_externo_4)+2L)[-1L],-1L)
#                       Vectorize(adjustcolor)(porcent_abs_externo_3,alpha.f=al)})



colores_ext <- rep("#5D93FF",length(unlist(col_ext)))
colores_ext <- ifelse(grepl("Algo",exterior$Nivel2),"#003399",colores_ext)

colores_ext_2 <- rep("#409B31",length(unlist(col_ext_2)))
colores_ext_2 <- ifelse(grepl("Leche",exterior_2$Nivel3),"#83D476",colores_ext_2)

colores_ext_3 <- rep("#E6F765",length(unlist(col_ext_3)))
colores_ext_3 <- ifelse(grepl(" - Bakery",exterior_3$Nivel4),"#D3DF7B",colores_ext_3)
colores_ext_3 <- ifelse(grepl("Solo",exterior_3$Nivel4),"#FFFFFF",colores_ext_3)
colores_ext_3 <- ifelse(grepl(" - Negro",exterior_3$Nivel4),"#9E9A00",colores_ext_3)


colores_ext_4 <- rep("#FFFFFF",length(exterior_4))
colores_ext_4 <- ifelse(grepl(" - Sandwich",exterior_4$Nivel5),"#BE3095",colores_ext_4)
colores_ext_4 <- ifelse(grepl(" - Caramelo",exterior_4$Nivel5),"#D19FC5",colores_ext_4)


library(stringr)
exterior$Nivel2 <-gsub("LLevar - ","", exterior$Nivel2);exterior$Nivel2 <-gsub("Local - ","", exterior$Nivel2)

exterior_2$Nivel3 <-gsub("LLevar - Algo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Algo - ","", exterior_2$Nivel3)
exterior_2$Nivel3 <-gsub("LLevar - Solo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Algo - ","", exterior_2$Nivel3)
exterior_2$Nivel3 <-gsub("Local - Solo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Solo - ","", exterior_2$Nivel3)

exterior_3$Nivel4 <- case_when(grepl("Sin_Bakery",exterior_3$Nivel4)~"Sin Bakery",
                               grepl(" - Bakery",exterior_3$Nivel4)~"Bakery",
                               grepl(" - Negro",exterior_3$Nivel4)~"Negro",
                               TRUE~"NA")

exterior_4$Nivel5 <- case_when(grepl("Sin_Sandwich",exterior_4$Nivel5)~"Sin Sandwich",
                               grepl("- Sandwich",exterior_4$Nivel5)~"Sandwich",
                               grepl("- Caramelo",exterior_4$Nivel5)~"Caramelo",
                               TRUE~"NA")



#tiff(filename = "prueba_tortas.tiff", width = 15, height = 15, units = 'in', res = 500)
plot.new()
#torta_ext_5=floating.pie(0.5,0.5,exterior_5$porcentaje_abs,radius=0.35,border="white",col=unlist(colores_ext_5))#,col=unlist(col_ext_5))
torta_ext_4=floating.pie(0.5,0.5,exterior_4$porcentaje_abs,radius=0.30,border="white",col=unlist(colores_ext_4))#,col=unlist(col_ext_4))
torta_ext_3=floating.pie(0.5,0.5,exterior_3$porcentaje_abs,radius=0.25,border="white",col=unlist(colores_ext_3))#,col=unlist(col_ext_3))
torta_ext_2=floating.pie(0.5,0.5,exterior_2$porcentaje_abs,radius=0.20,border="white",col=unlist(colores_ext_2))#,col=unlist(col_ext_2))
torta_ext=floating.pie(0.5,0.5,exterior$porcentaje_abs,radius=0.15,border="white",col=unlist(colores_ext))
torta_int=floating.pie(0.5,0.5,interior$porcentaje_abs,radius=0.10,border="white",col=unlist(col_int))
mtext(Titulo,side=3,adj=0,cex=2)
#showRatioThreshold = F
pie.labels(x=0.5, y=0.5, torta_int, paste0(interior$Nivel1,"\n", round(interior$porcentaje_abs*100),"%"),minangle=0.2,radius=0.03,cex=0.65,font=2,col="black")
pie.labels(x=0.5, y=0.5, torta_ext, paste0(exterior$Nivel2,"\n", round(exterior$mix_seg*100)," %"),minangle=0.2,radius=0.11,cex=0.65,font=2,col="black")
pie.labels(x=0.5, y=0.5, torta_ext_2, ifelse(exterior_2$porcentaje_abs<0.001,"",paste0(exterior_2$Nivel3,"\n", round(exterior_2$mix_seg*100)," %")),minangle=0.20,radius=0.16,cex=0.65,font=2,col="black")
pie.labels(x=0.5, y=0.5, torta_ext_3, ifelse(exterior_3$Nivel4=="NA" |exterior_3$porcentaje_abs<0.001 ,"",paste0(exterior_3$Nivel4,"\n", round(exterior_3$mix_seg*100)," %")),minangle=0,radius=0.21,cex=0.65,font=2,col="black")
pie.labels(x=0.5, y=0.5, torta_ext_4, ifelse(exterior_4$Nivel5 %in% c("Sandwich","Caramelo") & exterior_4$porcentaje_abs>0.001 ,paste0(exterior_4$Nivel5,"\n", round(exterior_4$mix_seg*100)," %"),""),minangle=0,radius=0.30,cex=0.65,font=2,col="black")
#pie.labels(x=0.5, y=0.5, torta_ext_5, paste0(exterior_5$Nivel6,"\n", round(exterior_5$mix_seg*100)," %"),minangle=0,radius=0.35,cex=0.65,font=2,col="black")
}
}

distribucion_horaria <- function(base_agrupada){
if(sum(base_agrupada$value[base_agrupada$variable %in% c("q_cafes_local",
                                                         "q_cafes_llevar")],na.rm=T)<3500){
  
}else{
grafico <- base_agrupada %>%
  dplyr::filter(variable %in% c("q_cafes_local_algo", "q_cafes_local", 
                         "q_cafes_local_solo", "q_cafes_llevar","q_cafes_local_algo_otros_sinbakery_negro")) %>%
  dplyr::group_by(variable) %>% dplyr::mutate(total_horario=sum(value,na.rm=T)) %>% dplyr::ungroup() %>% 
  dplyr::group_by(variable,hora) %>% 
  dplyr::summarise(value=(sum(value,na.rm=T)/max(total_horario))*100) %>% 
  ggplot() +
  aes(x = hora, y = value, colour = variable) +
  geom_line(size = 1.2) +
  scale_color_hue(direction = 1) +
  labs(
    x = "Hora",
    y = "Distribución %",
    title = "Distribución horaria",
    legend = "Conjunto"
  ) +scale_x_continuous(breaks = round(seq(min(base_agrupada$hora), max(base_agrupada$hora), by = 1),1)) +
  scale_y_continuous(breaks = seq(0, max(base_agrupada$value), by = 1)) +
  theme_bw()
print(grafico)
}
}

tortas_normalizadas <- function(base_agrupada,Titulo){
  interior <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_llevar","q_cafes_local")) %>% 
    dplyr::group_by(estacion) %>%
    dplyr::mutate(Cantidad=sum(value,na.rm=T)) %>% 
    dplyr::ungroup() %>% dplyr::group_by(Nivel1,estacion) %>% 
    dplyr::summarise(Cantidad_est=sum(value,na.rm=T),
                     Porcentaje_est=Cantidad_est/max(Cantidad)) %>%
    dplyr::group_by(Nivel1) %>% 
    dplyr::summarise(porcentaje_abs=median(Porcentaje_est,na.rm=T),Cantidad=median(Cantidad_est,na.rm=T))
sum(interior$porcentaje_abs)

    
  if(sum(interior$Cantidad)<3500){
    
  }else{
    exterior <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo","q_cafes_local_solo",
                                                               "q_cafes_llevar_algo","q_cafes_local_algo")) %>% 
      dplyr::group_by(estacion) %>% 
      dplyr::mutate(Cantidad_est_total=sum(value,na.rm=T)) %>% ungroup() %>% 
      dplyr::group_by(estacion,Nivel1) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::ungroup() %>% dplyr::group_by(Nivel1,Nivel2,estacion) %>% 
      dplyr::summarise(Cantidad_est=sum(value,na.rm=T),
                    Porcentaje_relativo=Cantidad_est/max(Cantidad_segmento),
                    Porcentaje_abs=Cantidad_est/max(Cantidad_est_total)) %>% 
      dplyr::group_by(Nivel2) %>% 
      dplyr::summarise(porcentaje_abs=median(Porcentaje_abs,na.rm=T),mix_seg=median(Porcentaje_relativo,na.rm=T),
                       Cantidad_segmento=sum(Cantidad_est,na.rm=T))
    sum(exterior$Cantidad_segmento)
    exterior$porcentaje_abs <- exterior$porcentaje_abs*(1/sum(exterior$porcentaje_abs))
    sum(exterior$porcentaje_abs)
    
    exterior_2 <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
                                                                  "q_cafes_llevar_algo_leche","q_cafes_local_algo_leche",
                                                                  "q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
                                                                  "q_cafes_llevar_algo_otros","q_cafes_local_algo_otros")) %>% 
      dplyr::group_by(estacion) %>%
      dplyr::mutate(Cantidad_est_total=sum(value,na.rm=T)) %>% ungroup() %>%  
      dplyr::group_by(estacion,Nivel2) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::ungroup() %>% dplyr::group_by(Nivel1,Nivel2,Nivel3,estacion) %>%
      dplyr::summarise(Cantidad_est=sum(value,na.rm=T),
                       Porcentaje_relativo=Cantidad_est/max(Cantidad_segmento),
                       Porcentaje_abs=Cantidad_est/max(Cantidad_est_total)) %>% 
      dplyr::group_by(Nivel3) %>% 
      dplyr::summarise(porcentaje_abs=median(Porcentaje_abs,na.rm=T),mix_seg=median(Porcentaje_relativo,na.rm=T),
                       Cantidad_segmento=sum(Cantidad_est,na.rm=T))
    sum(exterior_2$Cantidad_segmento)
    exterior_2$porcentaje_abs <- exterior_2$porcentaje_abs*(1/sum(exterior_2$porcentaje_abs))
    
    exterior_3 <- base_agrupada %>%
      dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
                                                                  "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
                                                                  "q_cafes_llevar_algo_leche_sinbakery","q_cafes_local_algo_leche_sinbakery",
                                                                  "q_cafes_llevar_algo_otros_sinbakery","q_cafes_local_algo_otros_sinbakery",
                                                                  "q_cafes_llevar_solo_otros_nonegro","q_cafes_local_solo_otros_nonegro",
                                                                  "q_cafes_llevar_solo_otros_negro1","q_cafes_local_solo_otros_negro1",
                                                                  "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche")) %>% 
      dplyr::group_by(estacion) %>%
      dplyr::mutate(Cantidad_est_total=sum(value,na.rm=T)) %>% ungroup() %>%  
      dplyr::group_by(estacion,Nivel3) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::ungroup() %>% dplyr::group_by(Nivel1,Nivel2,Nivel3,Nivel4,estacion) %>%
      dplyr::summarise(Cantidad_est=sum(value,na.rm=T),
                       Porcentaje_relativo=Cantidad_est/max(Cantidad_segmento),
                       Porcentaje_abs=Cantidad_est/max(Cantidad_est_total)) %>% 
      dplyr::group_by(Nivel4) %>% 
      dplyr::summarise(porcentaje_abs=median(Porcentaje_abs,na.rm=T),mix_seg=median(Porcentaje_relativo,na.rm=T),
                       Cantidad_segmento=sum(Cantidad_est,na.rm=T))
    sum(exterior_3$Cantidad_segmento)
    exterior_3$porcentaje_abs <- exterior_3$porcentaje_abs*(1/sum(exterior_3$porcentaje_abs))
    
    
    
    exterior_4 <- base_agrupada %>%
      dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
                                                                  "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
                                                                  "q_cafes_llevar_solo_leche_bakery","q_cafes_local_solo_leche_bakery",
                                                                  "q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
                                                                  "q_cafes_llevar_solo_otros_bakery","q_cafes_local_solo_otros_bakery",
                                                                  "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
                                                                  "q_cafes_llevar_solo_leche_sinbakery","q_cafes_local_solo_leche_sinbakery",
                                                                  "q_cafes_llevar_solo_otros_sinbakery","q_cafes_local_solo_otros_sinbakery",
                                                                  "q_cafes_llevar_algo_leche_sinbakery_sinsandwich_sin_caramelo","q_cafes_local_algo_leche_sinbakery_sinsandwich_sin_caramelo",
                                                                  "q_cafes_llevar_algo_otros_sinbakery_sinsandwich_sin_caramelo","q_cafes_local_algo_otros_sinbakery_sinsandwich_sin_caramelo",
                                                                  "q_cafes_llevar_algo_leche_sinbakery_sinsandwiches_caramelos","q_cafes_local_algo_leche_sinbakery_sinsandwiches_caramelos",
                                                                  "q_cafes_llevar_algo_otros_sinbakery_sinsandwiches_caramelos","q_cafes_local_algo_otros_sinbakery_sinsandwiches_caramelos",
                                                                  "q_cafes_llevar_algo_leche_sinbakery_sandwiches","q_cafes_local_algo_leche_sinbakery_sandwiches",
                                                                  "q_cafes_llevar_algo_otros_sinbakery_sandwiches","q_cafes_local_algo_otros_sinbakery_sandwiches")) %>% 
      dplyr::group_by(estacion) %>%
      dplyr::mutate(Cantidad_est_total=sum(value,na.rm=T)) %>% ungroup() %>%  
      dplyr::group_by(estacion,Nivel4) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::ungroup() %>% dplyr::group_by(Nivel1,Nivel2,Nivel3,Nivel4,Nivel5,estacion) %>%
      dplyr::summarise(Cantidad_est=sum(value,na.rm=T),
                       Porcentaje_relativo=Cantidad_est/max(Cantidad_segmento),
                       Porcentaje_abs=Cantidad_est/max(Cantidad_est_total)) %>% 
      dplyr::group_by(Nivel5) %>% 
      dplyr::summarise(porcentaje_abs=median(Porcentaje_abs,na.rm=T),mix_seg=median(Porcentaje_relativo,na.rm=T),
                       Cantidad_segmento=sum(Cantidad_est,na.rm=T))
    sum(exterior_4$Cantidad_segmento)
    exterior_4$porcentaje_abs <- exterior_4$porcentaje_abs*(1/sum(exterior_4$porcentaje_abs))
    # 
    # exterior_5 <- base_agrupada %>%
    #   dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_llevar_solo_otros","q_cafes_local_solo_otros",
    #                                                               "q_cafes_llevar_solo_leche","q_cafes_local_solo_leche",
    #                                                               "q_cafes_llevar_solo_leche_bakery","q_cafes_local_solo_leche_bakery",
    #                                                               "q_cafes_llevar_algo_leche_bakery","q_cafes_local_algo_leche_bakery",
    #                                                               "q_cafes_llevar_solo_otros_bakery","q_cafes_local_solo_otros_bakery",
    #                                                               "q_cafes_llevar_algo_otros_bakery","q_cafes_local_algo_otros_bakery",
    #                                                               "q_cafes_llevar_solo_leche_sinbakery","q_cafes_local_solo_leche_sinbakery",
    #                                                               "q_cafes_llevar_solo_otros_sinbakery","q_cafes_local_solo_otros_sinbakery",
    #                                                               "q_cafes_llevar_algo_leche_sinbakery_sinalfajor","q_cafes_local_algo_leche_sinbakery_sinalfajor",
    #                                                               "q_cafes_llevar_algo_otros_sinbakery_sinalfajor","q_cafes_local_algo_otros_sinbakery_sinalfajor",
    #                                                               "q_cafes_llevar_algo_leche_sinbakery_alfajor_cachafaz","q_cafes_local_algo_leche_sinbakery_alfajor_cachafaz",
    #                                                               "q_cafes_llevar_algo_otros_sinbakery_alfajor_cachafaz","q_cafes_local_algo_otros_sinbakery_alfajor_cachafaz",
    #                                                               "q_cafes_llevar_algo_leche_sinbakery_alfajor_sincachafaz","q_cafes_local_algo_leche_sinbakery_alfajor_sincachafaz",
    #                                                               "q_cafes_llevar_algo_otros_sinbakery_alfajor_sincachafaz","q_cafes_local_algo_otros_sinbakery_alfajor_sincachafaz")) %>% 
    #   dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
    #   dplyr::group_by(Nivel5) %>%
    #   dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
    #   ungroup() %>% 
    #   dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
    #   dplyr::group_by(Nivel6,variable) %>% 
    #   dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
    # 
    # sum(exterior_5$Cantidad_segmento)
    exterior_2 <- exterior_2[exterior_2$porcentaje_abs>0,]
    exterior_3 <- exterior_3[exterior_3$porcentaje_abs>0,]
    exterior_4 <- exterior_4[exterior_4$porcentaje_abs>0,]
    
    porcent_abs_externo <- exterior$porcentaje_abs
    porcent_abs_externo_2 <- exterior_2$porcentaje_abs
    porcent_abs_externo_3 <- exterior_3$porcentaje_abs
    porcent_abs_externo_4 <- exterior_4$porcentaje_abs
    # porcent_abs_externo_5 <- exterior_5$porcentaje_abs
    
    tabla <- table(exterior$Nivel2)[order(unique(exterior$Nivel2))]
    tabla_2 <- table(exterior_2$Nivel3)[order(unique(exterior_2$Nivel3))]
    tabla_3 <- table(exterior_3$Nivel4)[order(unique(exterior_3$Nivel4))]
    tabla_4 <- table(exterior_4$Nivel5)[order(unique(exterior_4$Nivel5))]
    # tabla_5 <- table(exterior_5$Nivel6)[order(unique(exterior_5$Nivel6))]
    
    
    #Armado grafico
    colores_ext <- rep("#5D93FF",length(unlist(col_ext)))
    colores_ext <- ifelse(grepl("Algo",exterior$Nivel2),"#003399",colores_ext)
    
    colores_ext_2 <- rep("#409B31",length(unlist(col_ext_2)))
    colores_ext_2 <- ifelse(grepl("Leche",exterior_2$Nivel3),"#83D476",colores_ext_2)
    
    colores_ext_3 <- rep("#E6F765",length(unlist(col_ext_3)))
    colores_ext_3 <- ifelse(grepl(" - Bakery",exterior_3$Nivel4),"#D3DF7B",colores_ext_3)
    colores_ext_3 <- ifelse(grepl("Solo",exterior_3$Nivel4),"#FFFFFF",colores_ext_3)
    colores_ext_3 <- ifelse(grepl(" - Negro",exterior_3$Nivel4),"#9E9A00",colores_ext_3)
    
    
    colores_ext_4 <- rep("#FFFFFF",length(exterior_4))
    colores_ext_4 <- ifelse(grepl(" - Sandwich",exterior_4$Nivel5),"#BE3095",colores_ext_4)
    colores_ext_4 <- ifelse(grepl(" - Caramelo",exterior_4$Nivel5),"#D19FC5",colores_ext_4)
    
    
    library(stringr)
    exterior$Nivel2 <-gsub("LLevar - ","", exterior$Nivel2);exterior$Nivel2 <-gsub("Local - ","", exterior$Nivel2)
    
    exterior_2$Nivel3 <-gsub("LLevar - Algo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Algo - ","", exterior_2$Nivel3)
    exterior_2$Nivel3 <-gsub("LLevar - Solo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Algo - ","", exterior_2$Nivel3)
    exterior_2$Nivel3 <-gsub("Local - Solo - ","", exterior_2$Nivel3);exterior_2$Nivel3 <-gsub("Local - Solo - ","", exterior_2$Nivel3)
    
    exterior_3$Nivel4 <- case_when(grepl("Sin_Bakery",exterior_3$Nivel4)~"Sin Bakery",
                                   grepl(" - Bakery",exterior_3$Nivel4)~"Bakery",
                                   grepl(" - Negro",exterior_3$Nivel4)~"Negro",
                                   TRUE~"NA")
    
    exterior_4$Nivel5 <- case_when(grepl("Sin_Sandwich",exterior_4$Nivel5)~"Sin Sandwich",
                                   grepl("- Sandwich",exterior_4$Nivel5)~"Sandwich",
                                   grepl("- Caramelo",exterior_4$Nivel5)~"Caramelo",
                                   TRUE~"NA")
    
    
    
    #tiff(filename = "prueba_tortas.tiff", width = 15, height = 15, units = 'in', res = 500)
    plot.new()
    #torta_ext_5=floating.pie(0.5,0.5,exterior_5$porcentaje_abs,radius=0.35,border="white",col=unlist(colores_ext_5))#,col=unlist(col_ext_5))
    torta_ext_4=floating.pie(0.5,0.5,exterior_4$porcentaje_abs,radius=0.30,border="white",col=unlist(colores_ext_4))#,col=unlist(col_ext_4))
    torta_ext_3=floating.pie(0.5,0.5,exterior_3$porcentaje_abs,radius=0.25,border="white",col=unlist(colores_ext_3))#,col=unlist(col_ext_3))
    torta_ext_2=floating.pie(0.5,0.5,exterior_2$porcentaje_abs,radius=0.20,border="white",col=unlist(colores_ext_2))#,col=unlist(col_ext_2))
    torta_ext=floating.pie(0.5,0.5,exterior$porcentaje_abs,radius=0.15,border="white",col=unlist(colores_ext))
    torta_int=floating.pie(0.5,0.5,interior$porcentaje_abs,radius=0.10,border="white",col=unlist(col_int))
    mtext(Titulo,side=3,adj=0,cex=2)
    #showRatioThreshold = F
    pie.labels(x=0.5, y=0.5, torta_int, paste0(interior$Nivel1,"\n", round(interior$porcentaje_abs*100),"%"),minangle=0.2,radius=0.03,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext, paste0(exterior$Nivel2,"\n", round(exterior$mix_seg*100)," %"),minangle=0.2,radius=0.11,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext_2, ifelse(exterior_2$porcentaje_abs<0.001,"",paste0(exterior_2$Nivel3,"\n", round(exterior_2$mix_seg*100)," %")),minangle=0.20,radius=0.16,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext_3, ifelse(exterior_3$Nivel4=="NA" |exterior_3$porcentaje_abs<0.001 ,"",paste0(exterior_3$Nivel4,"\n", round(exterior_3$mix_seg*100)," %")),minangle=0,radius=0.21,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext_4, ifelse(exterior_4$Nivel5 %in% c("Sandwich","Caramelo") & exterior_4$porcentaje_abs>0.001 ,paste0(exterior_4$Nivel5,"\n", round(exterior_4$mix_seg*100)," %"),""),minangle=0,radius=0.30,cex=0.65,font=2,col="black")
    #pie.labels(x=0.5, y=0.5, torta_ext_5, paste0(exterior_5$Nivel6,"\n", round(exterior_5$mix_seg*100)," %"),minangle=0,radius=0.35,cex=0.65,font=2,col="black")
  }
}

distribucion_horaria2 <- function(base_agrupada){
  if(sum(base_agrupada$value[base_agrupada$variable %in% c("q_cafes_local_algo_leche_bakery",
                                                            "q_cafes_local_algo_otros_sinbakery_negro_caramelos_total")],na.rm=T)<3500){
    
  }else{
    grafico <- base_agrupada %>%
      dplyr::filter(variable %in% c("q_cafes_local_algo_leche_bakery","q_cafes_local_algo_otros_sinbakery_negro_caramelos_total")) %>%
      dplyr::group_by(variable) %>% dplyr::mutate(total_horario=sum(value,na.rm=T)) %>% dplyr::ungroup() %>% 
      dplyr::group_by(variable,hora) %>% 
      dplyr::summarise(value=(sum(value,na.rm=T)/max(total_horario))*100) %>% 
      ggplot() +
      aes(x = hora, y = value, colour = variable) +
      geom_line(size = 1.2) +
      scale_color_hue(direction = 1) +
      labs(
        x = "Hora",
        y = "Distribución %",
        title = "Distribución horaria",
        legend = "Conjunto"
      ) +scale_x_continuous(breaks = round(seq(min(base_agrupada$hora), max(base_agrupada$hora), by = 1),1)) +
      scale_y_continuous(breaks = seq(0, max(base_agrupada$value), by = 1)) +
      theme_bw()
    print(grafico)
  }
}

tortas_q_cafes <- function(base_agrupada,Titulo){
  interior <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_llevar","q_cafes_local")) %>% 
    dplyr::group_by(Nivel1) %>% 
    dplyr::summarise(Cantidad=sum(value,na.rm=T)) %>% 
    mutate(porcentaje_abs=Cantidad/sum(Cantidad,na.rm=T))
  
  if(sum(interior$Cantidad)<3500){
    
  }else{
    exterior <- base_agrupada %>%
      dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_local_1","q_cafes_llevar_1",
                                                                  "q_cafes_llevar_mas_1","q_cafes_local_mas_1")) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::group_by(Nivel1) %>%
      dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
      ungroup() %>% 
      dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
      dplyr::group_by(Nivel2b,variable) %>% 
      dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
    sum(exterior$Cantidad_segmento)
    
    
    porcent_abs_externo <- exterior$porcentaje_abs
    
    tabla <- table(exterior$Nivel2b)[order(unique(exterior$Nivel2b))]

    # tabla_5 <- table(exterior_5$Nivel6)[order(unique(exterior_5$Nivel6))]
    
    
    #Armado grafico
    colores=c("#EC8080","#D52220")
    col_int <- rep_len(colores,length(interior$Nivel1))
    col_ext <- lapply(Map(rep,colores[seq_along(tabla)],tabla),
                      function(porcent_abs_externo){
                        al <- head(seq(0,1,length.out=length(porcent_abs_externo)+2L)[-1L],-1L)
                        Vectorize(adjustcolor)(porcent_abs_externo,alpha.f=al)})

    
    colores_ext <- rep("#5D93FF",length(unlist(col_ext)))
    colores_ext <- ifelse(grepl(">",exterior$Nivel2b),"#003399",colores_ext)
    
    library(stringr)
    exterior$Nivel2b <-gsub("LLevar - ","", exterior$Nivel2b);exterior$Nivel2b <-gsub("Local - ","", exterior$Nivel2b)

    #tiff(filename = "prueba_tortas.tiff", width = 15, height = 15, units = 'in', res = 500)
    plot.new()
    #torta_ext_5=floating.pie(0.5,0.5,exterior_5$porcentaje_abs,radius=0.35,border="white",col=unlist(colores_ext_5))#,col=unlist(col_ext_5))
    torta_ext=floating.pie(0.5,0.5,exterior$porcentaje_abs,radius=0.15,border="white",col=unlist(colores_ext))
    torta_int=floating.pie(0.5,0.5,interior$porcentaje_abs,radius=0.10,border="white",col=unlist(col_int))
    mtext(Titulo,side=3,adj=0,cex=2)
    #showRatioThreshold = F
    pie.labels(x=0.5, y=0.5, torta_int, paste0(interior$Nivel1,"\n", round(interior$porcentaje_abs*100),"%"),minangle=0.2,radius=0.03,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext, paste0(exterior$Nivel2b,"\n", round(exterior$mix_seg*100)," %"),minangle=0.2,radius=0.11,cex=0.65,font=2,col="black")
   #pie.labels(x=0.5, y=0.5, torta_ext_5, paste0(exterior_5$Nivel6,"\n", round(exterior_5$mix_seg*100)," %"),minangle=0,radius=0.35,cex=0.65,font=2,col="black")
  }
}

tortas_cafes_local <- function(base_agrupada,Titulo){

  
  interior <- base_agrupada %>% dplyr::filter(variable %in% c("q_cafes_local_algo_leche_bakery",
                                                              "q_cafes_local_algo_bakery_negro1",
                                                              "q_cafes_local_algo_otros_bakery_nonegro",
                                                              "q_cafes_local_algo_leche_sinbakery",
                                                              "q_cafes_local_algo_otros_sinbakery_nonegro",
                                                              "q_cafes_local_algo_otros_sinbakery_negro",
                                                              "q_cafes_local_solo_otros_nonegro",
                                                              "q_cafes_local_solo_otros_negro1",
                                                              "q_cafes_local_solo_leche")) %>% 
    dplyr::group_by(agrupacion_1) %>% 
    dplyr::summarise(Cantidad=sum(value,na.rm=T)) %>% 
    mutate(porcentaje_abs=Cantidad/sum(Cantidad,na.rm=T))
  
  if(sum(interior$Cantidad)<3500){
    
  }else{
    exterior <- base_agrupada %>%
      dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_local_algo_leche_bakery",
                                                                  "q_cafes_local_algo_bakery_negro1",
                                                                  "q_cafes_local_algo_otros_bakery_nonegro",
                                                                  "q_cafes_local_algo_leche_sinbakery",
                                                                  "q_cafes_local_algo_otros_sinbakery_nonegro",
                                                                  "q_cafes_local_algo_otros_sinbakery_negro",
                                                                  "q_cafes_local_solo_otros_nonegro",
                                                                  "q_cafes_local_solo_otros_negro1",
                                                                  "q_cafes_local_solo_leche")) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::group_by(agrupacion_1) %>%
      dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
      ungroup() %>% 
      dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
      dplyr::group_by(agrupacion_1,variable) %>% 
      dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
    sum(exterior$Cantidad_segmento)
    
    exterior_2 <- base_agrupada %>%
      dplyr::group_by(variable) %>% dplyr::filter(variable %in% c("q_cafes_local_algo_leche_bakery",
                                                                  "q_cafes_local_algo_bakery_negro1",
                                                                  "q_cafes_local_algo_otros_bakery_nonegro",
                                                                  "q_cafes_local_algo_leche_sinbakery",
                                                                  "q_cafes_local_algo_otros_sinbakery_nonegro",
                                                                  "q_cafes_local_algo_otros_sinbakery_negro_sincaramelos", 
                                                                  "q_cafes_local_algo_otros_sinbakery_negro_choco","q_cafes_local_algo_otros_sinbakery_negro_caramelonochoco",
                                                                  "q_cafes_local_solo_otros_nonegro",
                                                                  "q_cafes_local_solo_otros_negro1",
                                                                  "q_cafes_local_solo_leche")) %>% 
      dplyr::mutate(Cantidad_segmento=sum(value,na.rm=T)) %>% 
      dplyr::group_by(agrupacion_1,agrupacion_2) %>%
      dplyr::mutate(mix_seg=Cantidad_segmento/sum(value,na.rm=T)) %>% 
      ungroup() %>% 
      dplyr::mutate(porcentaje_abs=Cantidad_segmento/sum(value,na.rm=T))%>%
      dplyr::group_by(agrupacion_1,variable) %>% 
      dplyr::summarise(porcentaje_abs=max(porcentaje_abs),mix_seg=max(mix_seg),Cantidad_segmento=max(Cantidad_segmento))
    sum(exterior_2$Cantidad_segmento)
    
    
    porcent_abs_externo <- exterior$porcentaje_abs
    porcent_abs_externo_2 <- exterior_2$porcentaje_abs
    tabla <- table(exterior$agrupacion_1)[order(unique(exterior$agrupacion_1))]
    tabla2 <- table(exterior_2$agrupacion_1)[order(unique(exterior_2$agrupacion_1))]
    # tabla_5 <- table(exterior_5$Nivel6)[order(unique(exterior_5$Nivel6))]
    
    
    #Armado grafico
    colores=c("#EC8080","#D52220","#F4AAB8")
    col_int <- rep_len(colores,length(interior$agrupacion_1))
    
    col_ext <- lapply(Map(rep,colores[seq_along(tabla)],tabla),
                      function(porcent_abs_externo){
                        al <- head(seq(0,1,length.out=length(porcent_abs_externo)+2L)[-1L],-1L)
                        Vectorize(adjustcolor)(porcent_abs_externo,alpha.f=al)})
    
    col_ext_2 <- lapply(Map(rep,colores[seq_along(tabla2)],tabla2),
                      function(porcent_abs_externo_2){
                        al <- head(seq(0,1,length.out=length(porcent_abs_externo_2)+2L)[-1L],-1L)
                        Vectorize(adjustcolor)(porcent_abs_externo_2,alpha.f=al)})
    
    
    colores_ext <- rep("#5D93FF",length(unlist(col_ext)))
    colores_ext <- case_when(grepl("_leche",exterior$variable)~"#AEB3F8",
                             grepl("_negro",exterior$variable)~"#8266FA",
                             grepl("_nonegro",exterior$variable)~"#FFFFFF",
                             grepl("q_cafes_local_algo_otros_bakery",exterior$variable)~"#FFFFFF",
                             TRUE~colores_ext)
    
    colores_ext_2 <- rep("#FFFFFF",length(unlist(col_ext_2)))
    colores_ext_2 <- case_when(grepl("_caramelonochoco",exterior_2$variable)~"#DE92DC",
                              grepl("choco",exterior_2$variable)~"#872985",
                             TRUE~colores_ext_2)
    
    # library(stringr)
    # exterior$Nivel2b <-gsub("LLevar - ","", exterior$Nivel2b);exterior$Nivel2b <-gsub("Local - ","", exterior$Nivel2b)
    
    exterior$agrupacion_2 <- case_when(grepl("_leche",exterior$variable)~"Leche",
                                       grepl("_negro",exterior$variable)~"Negro",
                                       grepl("_nonegro",exterior$variable)~"No Negro",
                                       TRUE~"NA")
    
    exterior_2$agrupacion_2 <- case_when(
                                       grepl("_caramelonochoco",exterior_2$variable)~"Caramelos",
                                       grepl("choco",exterior_2$variable)~"Chocolate",
                                       TRUE~"NA")
    plot.new()
    torta_ext_2=floating.pie(0.5,0.5,exterior_2$porcentaje_abs,radius=0.20,border="white",col=unlist(colores_ext_2))
    torta_ext=floating.pie(0.5,0.5,exterior$porcentaje_abs,radius=0.15,border="white",col=unlist(colores_ext))
    torta_int=floating.pie(0.5,0.5,interior$porcentaje_abs,radius=0.10,border="white",col=unlist(col_int))
    mtext(Titulo,side=3,adj=0,cex=2)
    #showRatioThreshold = F
    pie.labels(x=0.5, y=0.5, torta_int, paste0(interior$agrupacion_1,"\n", round(interior$porcentaje_abs*100),"%"),minangle=0.2,radius=0.03,cex=0.65,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext, ifelse(!exterior$agrupacion_2 %in% c("No Negro","NA"),paste0(exterior$agrupacion_2,"\n", round(exterior$mix_seg*100)," %"),""),minangle=0.3,radius=0.11,cex=0.55,font=2,col="black")
    pie.labels(x=0.5, y=0.5, torta_ext_2, ifelse(!exterior_2$agrupacion_2 %in% c("NA"),paste0(exterior_2$agrupacion_2,"\n", round(exterior_2$mix_seg*100)," %"),""),minangle=0.3,radius=0.21,cex=0.50,font=2,col="black")
  }
}



for (i in sort(unique(na.omit(base_agrupada$Cluster_combinado)))){
  distribucion_horaria(base_agrupada[base_agrupada$Cluster_combinado==i,])
  print(i)
}

tortas(base_agrupada,"Total Red")

