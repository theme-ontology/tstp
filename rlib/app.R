# similar-stories-app

# preliminaries
palette(c("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999"))
require(shiny)
require(jsonlite)
require(curl)
source("helpers.r")

# read story metadata from web and do basic processing 
storydata <- fromJSON("http://ec2-52-56-219-127.eu-west-2.compute.amazonaws.com/tstp/webui/json.php?action=storydefinitions")
rownames(storydata) <- storydata[,1]
colnames(storydata) <- c("StoryID", "Title", "AirDate", "Summary")
storydata <- storydata[-1,]
story_id_index <- which(storydata[, "StoryID"] == "tos0x02")
storydata <- storydata[-story_id_index,]
story_id_index <- which(storydata[, "StoryID"] == "tng1x02")
storydata <- storydata[-story_id_index,]
story_id_index <- which(storydata[, "StoryID"] == "tng7x26")
storydata <- storydata[-story_id_index,]
story_ids <- SortStoryIDs(storydata[, "StoryID"])
no_of_stories <- length(story_ids)
summaries <- character(no_of_stories)
directors <- character(no_of_stories)
writers <- character(no_of_stories)
for(i in 1 : no_of_stories) {
  summaries[i] <- strsplit(storydata[i, "Summary"], split = "\n")[[1]][1]
  directors[i] <- strsplit(strsplit(storydata[i, "Summary"], split = "\n")[[1]][2], split = ": ")[[1]][2]
  writers[i] <- strsplit(strsplit(storydata[i, "Summary"], split = "\n")[[1]][3], split = ": ")[[1]][2]
}
storydata <- data.frame(storydata[,1:3], Writer = writers, Director = directors, Summary = summaries, stringsAsFactors = FALSE)
storydata <- storydata[story_ids,]

# read theme data from web and construct story list data structure to store story themes
themedata <- fromJSON("http://ec2-52-56-219-127.eu-west-2.compute.amazonaws.com/tstp/webui/json.php?action=metathemedata")
themes <- names(themedata[[1]])
no_of_themes <- length(themes)
storythemes <- vector("list", no_of_stories)
names(storythemes) <- story_ids
x <- vector("list", 3)
names(x) <- c("Choice", "Major", "Minor")
for(i in 1 : no_of_stories) {
  storythemes[[i]] <- x
}
for(i in 1 : no_of_themes) {
  theme <- themes[i]
  out <- themedata[[1]][theme][[1]]
  no_of_rows <- nrow(out)

  if(no_of_rows > 0) {
    for(j in 1 : no_of_rows) {
      story_id <- out[j, 1]
      theme_level <- out[j, 2]

      if(theme_level == "choice") {
        storythemes[[story_id]]$Choice <- append(storythemes[[story_id]]$Choice, theme)
      } else if(theme_level == "major") {
        storythemes[[story_id]]$Major <- append(storythemes[[story_id]]$Major, theme)
      } else if(theme_level == "minor") {
        storythemes[[story_id]]$Minor <- append(storythemes[[story_id]]$Minor, theme)
      }
    }
  }
}

# shiny ui
ui <- fluidPage(
  headerPanel('Similar story finder'),
  sidebarPanel(
    selectInput('story_id', 'Choose a story', rownames(storydata)),
    numericInput('min_overlap', 'Minimum overlap', 3, min = 1, max = 10),
    verbatimTextOutput(outputId = "summary")
  ),
  mainPanel(
    dataTableOutput(outputId = 'table1')
  )
)

# shiny server
server <- function(input, output) {

  data <- reactive({
    out <- data.frame(
      storydata[, c("StoryID", "Title")],
      Score = numeric(no_of_stories),
      Overlap = numeric(no_of_stories),
      stringsAsFactors = FALSE
    )

    mystory_themes <- unique(c(storythemes[[input$story_id]]$Choice, storythemes[[input$story_id]]$Major))

    for(i in 1 : no_of_stories) {
      refstory_themes <- unique(c(storythemes[[i]]$Choice, storythemes[[i]]$Major))
      out[i, "Overlap"] <- length(intersect(mystory_themes, refstory_themes))
      out[i, "Score"] <- length(intersect(mystory_themes, refstory_themes))/length(union(mystory_themes, refstory_themes))
    }

    out <- out[-which(out$StoryID == input$story_id),]
    out <- out[which(out$Overlap >= input$min_overlap),]
    out <- out[with(out, order(-Score)), ]
    return(out)
  })

  output$summary <- renderText({
    paste(paste0("Story ID: ", input$story_id),
      paste0("Title: ", storydata[input$story_id, "Title"]),
      paste0("Air Date: ", storydata[input$story_id, "AirDate"]),
      paste0("Writer: ", storydata[input$story_id, "Writer"]),
      paste0("Director: ", storydata[input$story_id, "Director"]),
      paste0("Summary: ", storydata[input$story_id, "Summary"], "\n"),
      paste0("Choice Themes:\n", paste0(storythemes[[input$story_id]]$Choice, collapse = "\n"), "\n"),
      paste0("Major Themes:\n", paste0(storythemes[[input$story_id]]$Major, collapse = "\n"), "\n"),
      paste0("Minor Themes:\n", paste0(storythemes[[input$story_id]]$Minor, collapse = "\n"), "\n"),
      sep = "\n"
    )
  })

  output$table1 <- renderDataTable({
    data()
  })

}

shinyApp(ui = ui, server = server)
