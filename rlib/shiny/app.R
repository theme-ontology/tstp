# similar-stories-app

# preliminaries
#palette(c("#E41A1C", "#377EB8", "#4DAF4A", "#984EA3", "#FF7F00", "#FFFF33", "#A65628", "#F781BF", "#999999"))
require(shiny)
require(jsonlite)
require(curl)
require(DT)
library(logitnorm)
source("helpers.r")
#source("/Users/paul/Desktop/tstpdm/data-analysis/Shiny-test-app/app/helpers.r")

# read story metadata from web and do basic processing 
storydata <- fromJSON("http://themeontology.org/json.php?action=storydefinitions")
#storydata <- fromJSON("/Users/paul/Desktop/tstpdm/data-analysis/Shiny-test-app/app/storydefinitions.json")
rownames(storydata) <- storydata[,1]
colnames(storydata) <- c("StoryID", "Title", "AirDate", "Summary")
storydata <- storydata[-1,]
story_id_index <- which(storydata[, "StoryID"] == "tos0x02")
storydata <- storydata[-story_id_index,]
story_id_index <- which(storydata[, "StoryID"] == "tng1x02")
storydata <- storydata[-story_id_index,]
story_id_index <- which(storydata[, "StoryID"] == "tng7x26")
storydata <- storydata[-story_id_index,]
keep_id_indices <- c(which(grepl("tos", storydata[, "StoryID"])), which(grepl("tas", storydata[, "StoryID"])), which(grepl("tng", storydata[, "StoryID"])))
storydata <- storydata[keep_id_indices,]
story_ids <- SortStoryIDs(storydata[, "StoryID"])
no_of_stories <- length(story_ids)
# summaries <- character(no_of_stories)
# directors <- character(no_of_stories)
# writers <- character(no_of_stories)
# for(i in 1 : no_of_stories) {
#  summaries[i] <- strsplit(storydata[i, "Summary"], split = "\n")[[1]][1]
#  directors[i] <- strsplit(strsplit(storydata[i, "Summary"], split = "\n")[[1]][2], split = ": ")[[1]][2]
#  writers[i] <- strsplit(strsplit(storydata[i, "Summary"], split = "\n")[[1]][3], split = ": ")[[1]][2]
# }
# storydata <- data.frame(storydata[,1:3], Summary = summaries, stringsAsFactors = FALSE)
storydata <- storydata[story_ids,]

# read minimal theme data from web and construct story list data structure to store story themes
themedata <- fromJSON("http://themeontology.org/json.php?action=metathemedata")
#themedata <- fromJSON("/Users/paul/Desktop/tstpdm/data-analysis/Shiny-test-app/app/metathemedata.json")
themes <- names(themedata[[1]])
no_of_themes <- length(themes)
storythemes <- vector("list", no_of_stories)
names(storythemes) <- story_ids
x <- vector("list", 2)
names(x) <- c("Central", "Peripheral")
for(i in 1 : no_of_stories) {
  storythemes[[i]] <- x
}
c_counts <- numeric(no_of_themes)
p_counts <- numeric(no_of_themes)
a_counts <- numeric(no_of_themes)
for(i in 1 : no_of_themes) {
  theme <- themes[i]
  out <- themedata[[1]][theme][[1]]
  no_of_rows <- nrow(out)

  if(no_of_rows > 0) {
    mystory_ids <- unique(out[, 1])
    no_of_mystory_ids <- length(mystory_ids)

    for(j in 1 : no_of_mystory_ids) {
      mystory_id <- mystory_ids[j]
      ids <- which(out[, 1] == mystory_id)
      levels <- out[ids, 2]
      no_of_levels <- length(levels)

      if(no_of_levels == 2) {
        if("choice" %in% levels && "major" %in% levels) {
          remove_id <- ids[which(levels == "major")]
          out <- out[-remove_id,]
        } else if("choice" %in% levels && "minor" %in% levels) {
          remove_id <- ids[which(levels == "minor")]
          out <- out[-remove_id,]
        }
      } else if(no_of_levels == 3) {
        remove_ids <- c(ids[which(levels == "major")], ids[which(levels == "minor")])
        out <- out[-remove_ids,]
      }
    }
  }

  if(no_of_rows > 0 && theme != "") {
    mystory_ids <- unique(out[, 1])
    no_of_mystory_ids <- length(mystory_ids) 
    a_counts[i] <- no_of_mystory_ids
    for(j in 1 : no_of_mystory_ids) {
      mystory_id <- mystory_ids[j]
      out2 <- out[which(out[, 1] == mystory_id), 2]
      c_counts[i] <- c_counts[i] + length(which(out2 == "choice")) + length(which(out2 == "major"))
      p_counts[i] <- p_counts[i] + length(which(out2 == "minor"))
    }

    for(j in 1 : no_of_rows) {
      story_id <- out[j, 1]
      theme_level <- out[j, 2]

      if(theme_level == "choice" || theme_level == "major") {
        storythemes[[story_id]]$Central <- append(storythemes[[story_id]]$Central, theme)
      } else if(theme_level == "minor") {
        storythemes[[story_id]]$Peripheral <- append(storythemes[[story_id]]$Peripheral, theme)
      }
    }
  }
}


# shiny ui
ui <- fluidPage(
  headerPanel('Similar story finder'),
  sidebarPanel(
    selectInput('story_id', 'Choose a story', paste0(rownames(storydata), ": ", storydata[, "Title"])),
    numericInput('min_overlap', 'Minimum overlap', 3, min = 1, max = 10)
  ),
  mainPanel(
    h4("Similar episodes"),
    DT::dataTableOutput(outputId = 'table1'),
    h4("Selected episode"),
    verbatimTextOutput(outputId = "summary")
  )
)

# shiny server
server <- function(input, output) {

  data <- reactive({
    N <- 278

    out <- data.frame(
      storydata[, c("StoryID", "Title")],
      Score = numeric(no_of_stories),
      Overlap = numeric(no_of_stories),
      stringsAsFactors = FALSE
    )

    story_id <- substring(input$story_id, 1, 7)

    mystory_themes <- unique(c(storythemes[[story_id]]$Central, storythemes[[story_id]]$Peripheral))

    # z <- (N - a_counts) / (N - 2)
    # z[which(z > 1)] <- 1
    # d <- plogitnorm(z, mu=1, sigma=1/3)
    # names(d) <- themes

    for(i in 1 : no_of_stories) {
      refstory_themes <- unique(c(storythemes[[i]]$Central, storythemes[[i]]$Peripheral))
      out[i, "Overlap"] <- length(intersect(mystory_themes, refstory_themes))
      out[i, "Score"] <- length(intersect(mystory_themes, refstory_themes))/length(union(mystory_themes, refstory_themes))
      INT <- intersect(mystory_themes, refstory_themes)
      UNI <- union(mystory_themes, refstory_themes)
      # if(length(INT) > 0) {
      #   out[i, "Score"] <- sum(as.numeric(d[INT]))/sum(as.numeric(d[UNI]))
      # } else {
      #   out[i, "Score"] <- 0
      # }
    }

    out <- out[-which(out$StoryID == story_id),]
    out <- out[which(out$Overlap >= input$min_overlap),]
    out <- out[with(out, order(-Score)), ]
    return(out)
  })

  # Generate table of similar stories
  output$table1 <- DT::renderDataTable(
    DT::datatable(
      data(), 
      options = list(pageLength = 10),
      rownames = FALSE
  ))

  # Generate a summary of the selected story
  output$summary <- renderText({
    story_id <- substring(input$story_id, 1, 7)
    paste(paste0("Story ID: ", story_id),
      paste0("Title: ", storydata[story_id, "Title"]),
      paste0("Air Date: ", storydata[story_id, "AirDate"]),
      #paste0("Writer: ", storydata[story_id, "Writer"]),
      #paste0("Director: ", storydata[story_id, "Director"]),
      paste0("Summary: ", storydata[story_id, "Summary"], "\n"),
      paste0("Central Themes:\n", paste0(storythemes[[story_id]]$Central, collapse = "\n"), "\n"),
      paste0("Peripheral Themes:\n", paste0(storythemes[[story_id]]$Peripheral, collapse = "\n"), "\n"),
      sep = "\n"
    )
  })
}

shinyApp(ui = ui, server = server)
