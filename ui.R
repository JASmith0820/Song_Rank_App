# DNSC 6203 Group Project - R Code for Shiny App USER INTERFACE
# Andrew Nichols, Jessica Smith, and Yahui Zhou 
# 26 November 2015

# To run this program:
# In R, change your working directory to the one with the ui.R and server.r code in it
# then type "runApp()" in the console, or put the path to the directory as an argument, thus:
# runApp('/home/vagrant/Programming_For_Analytics/Homework/Group_Project_Final')

# Helpful commands:
# getwd()   # To see the current working directory
# setwd('/home/vagrant/my_working_dir/DNSC_6211_Prog/GroupProjectMusic')   # Set working dir.
# dir()   # See names of files in current working directory

# install.packages('shiny')  # Install this for shiny if you haven't already
library(shiny)

s1=10

shinyUI(pageWithSidebar(
  headerPanel("Comparison of Popular Song Ranks"),
  sidebarPanel(
    sliderInput('CI', 'Enter Confidence Interval',value = 0.95, min = 0, max = 1, step = 0.01),
    sliderInput('equationSize', 'Enter Equation Size Multiplier',value = 0.5, min = 0, max = 1, step = 0.01),
    sliderInput('dotSize', 'Enter Dot Size Multiplier',value = 0.5, min = 0, max = 1, step = 0.01),
    sliderInput('plotSize', 'Enter Plot Range Multiplier',value = 1, min = 0, max = 3, step = 0.01)
  ),
  mainPanel(
    plotOutput('musicPlot1'),
    plotOutput('musicPlot2'),
    plotOutput('musicPlot3')
  )
))