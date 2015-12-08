# DNSC 6203 Group Project - R Code for Shiny App SERVER
# Andrew Nichols, Jessica Smith, and Yahui Zhou 
# 26 November 2015

library(ggplot2)
library(shiny)

#Read in the Billboard Hot 100 vs. Shazam Top 100 csv file into a data frame
df1 <- read.csv('billboardhot100_vs_shazamtop100.csv', header=T) 
x1 <- df1$billboard_rank
y1 <- df1$shazam_rank

#Read in the Shazam Hit Predictor vs. Billboard Hot 100 csv file into a data frame
df2 <- read.csv('shazamhitpredictor_vs_billboardhot100.csv', header=T) 

#Read in the Billboard Trending 140 vs. Billboard Hot 100 csv 
df3 <- read.csv('billboardtoptrending_vs_billboardhot100.csv', header=T)
x3 <- df3$billboard_top_trending_rank
y3 <- df3$billboard_hot_100_rank

shinyServer(
  function(input, output) {
    #Plot The Billboard Hot 100 vs. The Shazam Top 100
    output$musicPlot1 <- renderPlot({
      
      CI1 <- input$CI
      dotSize1 <- input$dotSize
      equationSize1 <- input$equationSize
      m1 <- input$plotSize
      
      # Source of linear equation label on plot with r-squared coefficient: http://goo.gl/K4yh and 
      # http://stackoverflow.com/questions/7549694/ggplot2-adding-regression-line-equation-and-r2-on-graph
      # This code calculates equation of the line for use in the plot
      lm_eqn <- function(df1){
        m <- lm(y1 ~ x1, df1);
        eq <- substitute(italic(y1) == a + b %.% italic(x1)*","~~italic(r)^2~"="~r2, 
                         list(a = format(coef(m)[1], digits = 2), 
                              b = format(coef(m)[2], digits = 2), 
                              r2 = format(summary(m)$r.squared, digits = 3)))
        as.character(as.expression(eq));                 
      }
      
      # Plot correlation of Billboard song rank (x-axis) vs. Shazam song rank (y-axis)
          # Size of point labels in plot
      s2 <- 4*dotSize1     # Size of points themselves
      s3 <- 8*equationSize1     # Size of equation in plot
      
      # Confidence interval for best-fit line determined by user
      ggplot(df1, aes(x=billboard_rank, y=shazam_rank, label=song))+         
        geom_point(aes(color=artist), size=s2)+
        geom_text(aes(label=song, color=artist, size=10),hjust=-0.15, vjust=0.5)+
        geom_text(aes(label=artist, color=artist, size=10),hjust=-0.15, vjust=-.5)+
        geom_text(aes(label=paste0('(',billboard_rank,',',shazam_rank,')'), color=artist, size=10, hjust=1.3, vjust=0))+
        geom_text(x = 4, y = 24, label = lm_eqn(df1), color='blue', size=s3, parse = TRUE)+
        geom_text(x = 4, y = 22, color='blue', size=s3,
                  label=paste0('Confidence Interval = ',CI1))+
        labs(title="Billboard Hot 100 vs. Shazam Top 100")+ 
        labs(x="Billboard Song Rank", y="Shazam Song Rank")+
        geom_smooth(method="lm", fullrange=TRUE, size=.5, se=TRUE, level=CI1, alpha=0.18)+
        theme_bw()+
        xlim(-5*m1, 50*m1)+
        ylim(-5*m1, 45*m1)+
        theme(legend.position="none")
    } )
    
    #Plot The Shazam Hit Predictor vs. The Billboard Hot 100
    output$musicPlot2 <- renderPlot({
      
      numHits <- length(which(df2$hit==1))
      numNotHits <- length(which(df2$hit==2))
      
      hitData <- c(numHits,numNotHits)
      pct <- round(hitData/sum(hitData)*100)
      hitLabels <- c('Hit','Not a hit')
      hitLabels <- paste(hitLabels, pct)
      hitLabels <- paste(hitLabels, "%",sep="")
      colors <- c("forestgreen","firebrick")
      pie(hitData, labels = hitLabels, col = colors
          ,main = "Percent of Shazam Predicted Hits (20 Songs) in \nBillboard Hot 100 One Week Later"
          ,cex = 1.5
          ,cex.main = 1.2)
    })
      
    #Plot the Billboard Top Trending vs the Billboard Top 100
    output$musicPlot3 <- renderPlot({
      
      numHits <- length(which(df3$hit==1))
      numNotHits <- length(which(df3$hit==2))
      
      hitData <- c(numHits,numNotHits)
      pct <- round(hitData/sum(hitData)*100)
      hitLabels <- c('Hit','Not a hit')
      hitLabels <- paste(hitLabels, pct)
      hitLabels <- paste(hitLabels, "%",sep="")
      colors <- c("forestgreen","firebrick")
      pie(hitData, labels = hitLabels, col = colors
          ,main = "Percent of Billboard Trending 140 (Top 20 Songs Only) in \nBillboard Hot 100 One Week Later"
          ,cex = 1.5
          ,cex.main = 1.2)
    })
  }
)