SortStoryIDs <- function(story_ids) {
	story_ids <- sort(story_ids)
	no_of_story_ids <- length(story_ids)
	series_ids <- character(no_of_story_ids)
	episode_ids_sort <- character(no_of_story_ids)
	for( i in 1 : no_of_story_ids ) {
		series_ids[ i ] <- substring(story_ids[ i ], 1, 3)
	}
	tos_ids <- which( series_ids == "tos" )
	tas_ids <- which( series_ids == "tas" )
	tng_ids <- which( series_ids == "tng" )
	story_ids_sort <- c(story_ids[tos_ids], story_ids[tas_ids], story_ids[tng_ids])
	return(story_ids_sort)
}

StoryIDsToUppercase <- function(story_ids) {
	story_ids <- gsub("tos", "TOS", story_ids)
	story_ids <- gsub("tas", "TAS", story_ids)
	story_ids <- gsub("tng", "TNG", story_ids)
	return(story_ids)
}

StoryIDsToLowercase <- function(story_ids) {
	story_ids <- gsub("TOS", "tos", story_ids)
	story_ids <- gsub("TAS", "tas", story_ids)
	story_ids <- gsub("TNG", "tng", story_ids)
	return(story_ids)
}

GetAllStoryIDs <- function() {
	story_ids <- c("tos0x01", "tos1x01", "tos1x02", "tos1x03", "tos1x04", "tos1x05", "tos1x06", "tos1x07", "tos1x08", "tos1x09", "tos1x10", "tos1x11", "tos1x12", "tos1x13", "tos1x14", "tos1x15", "tos1x16", "tos1x17", "tos1x18", "tos1x19", "tos1x20", "tos1x21", "tos1x22", "tos1x23", "tos1x24", "tos1x25", "tos1x26", "tos1x27", "tos1x28", "tos1x29", "tos2x01", "tos2x02", "tos2x03", "tos2x04", "tos2x05", "tos2x06", "tos2x07", "tos2x08", "tos2x09", "tos2x10", "tos2x11", "tos2x12", "tos2x13", "tos2x14", "tos2x15", "tos2x16", "tos2x17", "tos2x18", "tos2x19", "tos2x20", "tos2x21", "tos2x22", "tos2x23", "tos2x24", "tos2x25", "tos2x26", "tos3x01", "tos3x02", "tos3x03", "tos3x04", "tos3x05", "tos3x06", "tos3x07", "tos3x08", "tos3x09", "tos3x10", "tos3x11", "tos3x12", "tos3x13", "tos3x14", "tos3x15", "tos3x16", "tos3x17", "tos3x18", "tos3x19", "tos3x20", "tos3x21", "tos3x22", "tos3x23", "tos3x24", "tas1x01", "tas1x02", "tas1x03", "tas1x04", "tas1x05", "tas1x06", "tas1x07", "tas1x08", "tas1x09", "tas1x10", "tas1x11", "tas1x12", "tas1x13", "tas1x14", "tas1x15", "tas1x16", "tas2x01", "tas2x02", "tas2x03", "tas2x04", "tas2x05", "tas2x06", "tng1x01", "tng1x03", "tng1x04", "tng1x05", "tng1x06", "tng1x07", "tng1x08", "tng1x09", "tng1x10", "tng1x11", "tng1x12", "tng1x13", "tng1x14", "tng1x15", "tng1x16", "tng1x17", "tng1x18", "tng1x19", "tng1x20", "tng1x21", "tng1x22", "tng1x23", "tng1x24", "tng1x25", "tng1x26", "tng2x01", "tng2x02", "tng2x03", "tng2x04", "tng2x05", "tng2x06", "tng2x07", "tng2x08", "tng2x09", "tng2x10", "tng2x11", "tng2x12", "tng2x13", "tng2x14", "tng2x15", "tng2x16", "tng2x17", "tng2x18", "tng2x19", "tng2x20", "tng2x21", "tng2x22", "tng3x01", "tng3x02", "tng3x03", "tng3x04", "tng3x05", "tng3x06", "tng3x07", "tng3x08", "tng3x09", "tng3x10", "tng3x11", "tng3x12", "tng3x13", "tng3x14", "tng3x15", "tng3x16", "tng3x17", "tng3x18", "tng3x19", "tng3x20", "tng3x21", "tng3x22", "tng3x23", "tng3x24", "tng3x25", "tng3x26", "tng4x01", "tng4x02", "tng4x03", "tng4x04", "tng4x05", "tng4x06", "tng4x07", "tng4x08", "tng4x09", "tng4x10", "tng4x11", "tng4x12", "tng4x13", "tng4x14", "tng4x15", "tng4x16", "tng4x17", "tng4x18", "tng4x19", "tng4x20", "tng4x21", "tng4x22", "tng4x23", "tng4x24", "tng4x25", "tng4x26", "tng5x01", "tng5x02", "tng5x03", "tng5x04", "tng5x05", "tng5x06", "tng5x07", "tng5x08", "tng5x09", "tng5x10", "tng5x11", "tng5x12", "tng5x13", "tng5x14", "tng5x15", "tng5x16", "tng5x17", "tng5x18", "tng5x19", "tng5x20", "tng5x21", "tng5x22", "tng5x23", "tng5x24", "tng5x25", "tng5x26", "tng6x01", "tng6x02", "tng6x03", "tng6x04", "tng6x05", "tng6x06", "tng6x07", "tng6x08", "tng6x09", "tng6x10", "tng6x11", "tng6x12", "tng6x13", "tng6x14", "tng6x15", "tng6x16", "tng6x17", "tng6x18", "tng6x19", "tng6x20", "tng6x21", "tng6x22", "tng6x23", "tng6x24", "tng6x25", "tng6x26", "tng7x01", "tng7x02", "tng7x03", "tng7x04", "tng7x05", "tng7x06", "tng7x07", "tng7x08", "tng7x09", "tng7x10", "tng7x11", "tng7x12", "tng7x13", "tng7x14", "tng7x15", "tng7x16", "tng7x17", "tng7x18", "tng7x19", "tng7x20", "tng7x21", "tng7x22", "tng7x23", "tng7x24", "tng7x25")
	return(story_ids)
}