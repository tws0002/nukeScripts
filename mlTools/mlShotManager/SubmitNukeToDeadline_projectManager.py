import os, sys, re, traceback
import ast
import threading
import time
#nuke.Root().lastFrame()
#nuke.Root().firstFrame()
#writeNodes


try:
	import ConfigParser
except:
	print( "Could not load ConfigParser module, sticky settings will not be loaded/saved" )

import nuke, nukescripts

dialog = None
deadlineCommand = None
nukeScriptPath = None
deadlineHome = None

shotgunKVPs = None

multiJobResults = ""

class DeadlineDialog( nukescripts.PythonPanel ):
	pools = []
	groups = []
	
	def __init__( self, pools, groups ):
		nukescripts.PythonPanel.__init__( self, "Submit To Deadline", "com.thinkboxsoftware.software.deadlinedialog" )
		
		self.setMinimumSize( 600, 640 )
		
		self.jobTab = nuke.Tab_Knob( "jobOptionsTab", "Job Options" )
		self.addKnob( self.jobTab )
		
		##########################################################################################
		## Job Description
		##########################################################################################
		
		# Job Name
		self.jobName = nuke.String_Knob( "jobName", "Job Name" )
		self.addKnob( self.jobName )
		self.jobName.setValue( "Untitled" )
		
		# Comment
		self.comment = nuke.String_Knob( "comment", "Comment" )
		self.addKnob( self.comment )
		self.comment.setValue( "" )
		
		# Department
		self.department = nuke.String_Knob( "department", "Department" )
		self.addKnob( self.department )
		self.department.setValue( "" )
		
		# Separator
		self.separator1 = nuke.Text_Knob( "separator1", "" )
		self.addKnob( self.separator1 )
		
		##########################################################################################
		## Job Scheduling
		##########################################################################################
		
		# Pool
		self.pool = nuke.Enumeration_Knob( "pool", "Pool", pools )
		self.addKnob( self.pool )
		self.pool.setValue( "none" )
		
		# Group
		self.group = nuke.Enumeration_Knob( "group", "Group", groups )
		self.addKnob( self.group )
		self.group.setValue( "none" )
		
		# Priority
		self.priority = nuke.Int_Knob( "priority", "Priority" )
		self.addKnob( self.priority )
		self.priority.setValue( 50 )
		
		# Task Timeout
		self.taskTimeout = nuke.Int_Knob( "taskTimeout", "Task Timeout" )
		self.addKnob( self.taskTimeout )
		self.taskTimeout.setValue( 0 )
		
		# Auto Task Timeout
		self.autoTaskTimeout = nuke.Boolean_Knob( "autoTaskTimeout", "Enable Auto Task Timeout" )
		self.addKnob( self.autoTaskTimeout )
		self.autoTaskTimeout.setValue( False )
		
		# Concurrent Tasks
		self.concurrentTasks = nuke.Int_Knob( "concurrentTasks", "Concurrent Tasks" )
		self.addKnob( self.concurrentTasks )
		self.concurrentTasks.setValue( 1 )
		
		# Limit Concurrent Tasks
		self.limitConcurrentTasks = nuke.Boolean_Knob( "limitConcurrentTasks", "Limit Tasks To Slave's Task Limit" )
		self.addKnob( self.limitConcurrentTasks )
		self.limitConcurrentTasks.setValue( False )
		
		# Machine Limit
		self.machineLimit = nuke.Int_Knob( "machineLimit", "Machine Limit" )
		self.addKnob( self.machineLimit )
		self.machineLimit.setValue( 0 )
		
		# Machine List Is Blacklist
		self.isBlacklist = nuke.Boolean_Knob( "isBlacklist", "Machine List Is A Blacklist" )
		self.addKnob( self.isBlacklist )
		self.isBlacklist.setValue( False )
		
		# Machine List
		self.machineList = nuke.String_Knob( "machineList", "Machine List" )
		self.addKnob( self.machineList )
		self.machineList.setValue( "" )
		
		self.machineListButton = nuke.PyScript_Knob( "machineListButton", "Browse" )
		self.addKnob( self.machineListButton )
		
		# Limit Groups
		self.limitGroups = nuke.String_Knob( "limitGroups", "Limit Groups" )
		self.addKnob( self.limitGroups )
		self.limitGroups.setValue( "" )
		
		self.limitGroupsButton = nuke.PyScript_Knob( "limitGroupsButton", "Browse" )
		self.addKnob( self.limitGroupsButton )
		
		# Dependencies
		self.dependencies = nuke.String_Knob( "dependencies", "Dependencies" )
		self.addKnob( self.dependencies )
		self.dependencies.setValue( "" )
		
		self.dependenciesButton = nuke.PyScript_Knob( "dependenciesButton", "Browse" )
		self.addKnob( self.dependenciesButton )
		
		# On Complete
		self.onComplete = nuke.Enumeration_Knob( "onComplete", "On Job Complete", ("Nothing", "Archive", "Delete") )
		self.addKnob( self.onComplete )
		self.onComplete.setValue( "Nothing" )
		
		# Submit Suspended
		self.submitSuspended = nuke.Boolean_Knob( "submitSuspended", "Submit Job As Suspended" )
		self.addKnob( self.submitSuspended )
		self.submitSuspended.setValue( False )
		
		# Separator
		self.separator1 = nuke.Text_Knob( "separator1", "" )
		self.addKnob( self.separator1 )
		
		##########################################################################################
		## Nuke Options
		##########################################################################################
		
		# Frame List
		self.frameListMode = nuke.Enumeration_Knob( "frameListMode", "Frame List", ("Global", "Input", "Custom") )
		self.addKnob( self.frameListMode )
		self.frameListMode.setValue( "Global" )
		
		self.frameList = nuke.String_Knob( "frameList", "" )
		self.frameList.clearFlag(nuke.STARTLINE)
		self.addKnob( self.frameList )
		self.frameList.setValue( "" )
		
		# Chunk Size
		self.chunkSize = nuke.Int_Knob( "chunkSize", "Frames Per Task" )
		self.addKnob( self.chunkSize )
		self.chunkSize.setValue( 10 )
		
		# NukeX
		self.useNukeX = nuke.Boolean_Knob( "useNukeX", "Render With NukeX" )
		self.addKnob( self.useNukeX )
		self.useNukeX.setValue( False )
		
		# Threads
		self.threads = nuke.Int_Knob( "threads", "Render Threads" )
		self.addKnob( self.threads )
		self.threads.setValue( 0 )
		
		# Continue On Error
		self.continueOnError = nuke.Boolean_Knob( "continueOnError", "Continue On Error" )
		self.addKnob( self.continueOnError )
		self.continueOnError.setValue( False )
		
		# Memory Usage
		self.memoryUsage = nuke.Int_Knob( "memoryUsage", "Maximum RAM Usage" )
		self.addKnob( self.memoryUsage )
		self.memoryUsage.setValue( 0 )
		
		#Batch Mode
		self.batchMode = nuke.Boolean_Knob( "batchMode", "Use Batch Mode" )
		self.addKnob( self.batchMode )
		self.batchMode.setValue( False )
		
		# Build
		self.build = nuke.Enumeration_Knob( "build", "Build To Force", ("None", "32bit", "64bit") )
		self.addKnob( self.build )
		self.build.setValue( "None" )
		
		# Submit Scene
		self.submitScene = nuke.Boolean_Knob( "submitScene", "Submit Nuke Script File With Job" )
		self.addKnob( self.submitScene )
		self.submitScene.setValue( False )
		
		# Separator
		self.separator1 = nuke.Text_Knob( "separator1", "" )
		self.addKnob( self.separator1 )
		
		# Separate Jobs
		self.separateJobs = nuke.Boolean_Knob( "separateJobs", "Submit Write Nodes As Separate Jobs" )
		self.addKnob( self.separateJobs )
		self.separateJobs.setValue( False )
		
		# Use Node's Frame List
		self.useNodeRange = nuke.Boolean_Knob( "useNodeRange", "Use Node's Frame List" )
		self.addKnob( self.useNodeRange )
		self.useNodeRange.setValue( True )
		
		# Only Submit Selected Nodes
		self.selectedOnly = nuke.Boolean_Knob( "selectedOnly", "Selected Nodes Only" )
		self.selectedOnly.setFlag(nuke.STARTLINE)
		self.addKnob( self.selectedOnly )
		self.selectedOnly.setValue( False )
		
        #write nodes here
        
		# Only Submit Read File Nodes
		self.readFileOnly = nuke.Boolean_Knob( "readFileOnly", "Nodes With 'Read File' Enabled Only" )
		self.addKnob( self.readFileOnly )
		self.readFileOnly.setValue( False )
		
		##########################################################################################
		## Shotgun Options
		##########################################################################################
		
		self.shotgunDraftTab = nuke.Tab_Knob( "shotgunDraftTab", "Shotgun/Draft" )
		self.addKnob( self.shotgunDraftTab )
		
		self.connectToShotgunButton = nuke.PyScript_Knob( "connectToShotgunButton", "Connect to Shotgun..." )
		self.addKnob( self.connectToShotgunButton )
		
		self.useShotgunInfo = nuke.Boolean_Knob( "useShotgunInfo", "Submit Shotgun Info With Job" )
		self.addKnob( self.useShotgunInfo )
		self.useShotgunInfo.setEnabled( False )
		self.useShotgunInfo.setValue( False )
		
		self.shotgunVersion = nuke.String_Knob( "shotgunVersion", "Version Name" )
		self.addKnob( self.shotgunVersion )
		self.shotgunVersion.setValue( "" )
		self.shotgunVersion.setEnabled( False )
		
		self.shotgunDescription = nuke.String_Knob( "shotgunDescription", "Description" )
		self.addKnob( self.shotgunDescription )
		self.shotgunDescription.setValue( "" )
		self.shotgunDescription.setEnabled( False )
		
		self.shotgunInfo = nuke.Multiline_Eval_String_Knob( "shotgunInfo", "Selected Entity" )
		self.addKnob( self.shotgunInfo )
		self.shotgunInfo.setEnabled( False )
		
		##########################################################################################
		## Draft Options
		##########################################################################################
		
		#~ self.draftTab = nuke.Tab_Knob( "draftTab", "Draft" )
		#~ self.addKnob( self.draftTab )
		
		self.draftSeparator1 = nuke.Text_Knob( "draftSeparator1", "" )
		self.addKnob( self.draftSeparator1 )
		
		self.submitDraftJob = nuke.Boolean_Knob( "submitDraftJob", "Submit Dependent Draft Job" )
		self.addKnob( self.submitDraftJob )
		self.submitDraftJob.setValue( False )
		
		self.uploadToShotgun = nuke.Boolean_Knob( "uploadToShotgun", "Upload to Shotgun" )
		self.addKnob( self.uploadToShotgun )
		self.uploadToShotgun.setValue( True )
		self.uploadToShotgun.setEnabled( False )
		
		self.templatePath = nuke.File_Knob( "templatePath", "Draft Template" )
		self.addKnob( self.templatePath )
		self.templatePath.setEnabled( False )
		
		self.draftUser = nuke.String_Knob( "draftUser", "User" )
		self.addKnob( self.draftUser )
		self.draftUser.setValue( "" )
		self.draftUser.setEnabled( False )
		
		self.draftEntity = nuke.String_Knob( "draftEntity", "Entity" )
		self.addKnob( self.draftEntity )
		self.draftEntity.setValue( "" )
		self.draftEntity.setEnabled( False )
		
		self.draftVersion = nuke.String_Knob( "draftVersion", "Version" )
		self.addKnob( self.draftVersion )
		self.draftVersion.setValue( "" )
		self.draftVersion.setEnabled( False )
		
		self.useShotgunDataButton = nuke.PyScript_Knob( "useShotgunDataButton", "Use Shotgun Data" )
		self.useShotgunDataButton.setFlag(nuke.STARTLINE)
		self.addKnob( self.useShotgunDataButton )
		self.useShotgunDataButton.setEnabled( False )
		
		
	def knobChanged( self, knob ):
		global draftTemplateField
		global shotgunValues
		global shotgunKVPs
		
		if knob == self.machineListButton:
			GetMachineListFromDeadline()
			
		if knob == self.limitGroupsButton:
			GetLimitGroupsFromDeadline()
		
		if knob == self.dependenciesButton:
			GetDependenciesFromDeadline()
		
		if knob == self.frameList:
			self.frameListMode.setValue( "Custom" )
		
			
		if knob == self.separateJobs:
			#self.readFileOnly.setEnabled( self.separateJobs.value() )
			#self.selectedOnly.setEnabled( self.separateJobs.value() )
			self.useNodeRange.setEnabled( self.separateJobs.value() )
			
			self.frameList.setEnabled( not(self.separateJobs.value() and self.useNodeRange.value()) )
		
		if knob == self.useNodeRange:
			self.frameListMode.setEnabled( not(self.separateJobs.value() and self.useNodeRange.value()) )
			self.frameList.setEnabled( not(self.separateJobs.value() and self.useNodeRange.value()) )
		
		if knob == self.connectToShotgunButton:
			GetShotgunInfo()
		
		if knob == self.useShotgunDataButton:
			user = shotgunKVPs.get( 'UserName', "" )
			task = shotgunKVPs.get( 'TaskName', "" )
			project = shotgunKVPs.get( 'ProjectName', "" )
			entity = shotgunKVPs.get( 'EntityName', "" )
			version = shotgunKVPs.get( 'VersionName', "" )
			draftTemplate = shotgunKVPs.get( 'DraftTemplate', "" )
			
			#set any relevant values
			self.draftUser.setValue( user )
			self.draftVersion.setValue( version )
			
			if task.strip() != "":
				self.draftEntity.setValue( "%s" % task )
			elif project.strip() != "" and entity.strip() != "":
				self.draftEntity.setValue( "%s > %s" % (project, entity) )
				
			if draftTemplate.strip() != "" and draftTemplate != "None":
				self.templatePath.setValue( draftTemplate )
		
		if knob == self.shotgunVersion:
			shotgunKVPs['VersionName'] = self.shotgunVersion.value()
		
		if knob == self.shotgunDescription:
			shotgunKVPs['Description'] = self.shotgunDescription.value()
		
		if knob == self.useShotgunInfo:
			self.shotgunVersion.setEnabled( self.useShotgunInfo.value() )
			self.shotgunDescription.setEnabled( self.useShotgunInfo.value() )
			
			#draft controls that require shotgun to be used
			self.uploadToShotgun.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
			self.useShotgunDataButton.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
		
		
		if knob == self.submitDraftJob:
			self.templatePath.setEnabled( self.submitDraftJob.value() )
			self.draftUser.setEnabled( self.submitDraftJob.value() )
			self.draftEntity.setEnabled( self.submitDraftJob.value() )
			self.draftVersion.setEnabled( self.submitDraftJob.value() )
			
			#these two settings also depend on shotgun being enabled
			self.useShotgunDataButton.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
			self.uploadToShotgun.setEnabled( self.useShotgunInfo.value() and self.submitDraftJob.value() )
			
	def ShowDialog( self ):
		return nukescripts.PythonPanel.showModalDialog( self )


def GetShotgunInfo():
	global dialog
	global nukeScriptPath
	global shotgunValues
	global shotgunJobSettings
	global shotgunKVPs
	
	tempKVPs = {}
	
	shotgunPath = nukeScriptPath.replace( "/submission/Nuke", "" ) + "/events/Shotgun"
	shotgunScript = shotgunPath + "/ShotgunUI.py"
	
	stdout = None
	if os.path.exists( "/Applications/Deadline/Resources/bin/deadlinecommand" ):
		stdout = os.popen( '/Applications/Deadline/Resources/bin/deadlinecommand ExecuteScript "%s" Nuke' % shotgunScript )
	else:
		stdout = os.popen( 'deadlinecommand ExecuteScript "%s" Nuke' % shotgunScript )
		
	#outputLines = stdout.readlines()
	output = stdout.read()
	outputLines = output.splitlines()
	stdout.close()
	
	for line in outputLines:
		line = line.strip()
		
		tokens = line.split( '=', 1 )
		
		if len( tokens ) > 1:
			key = tokens[0]
			value = tokens[1]
			
			tempKVPs[key] = value
	
	if len( tempKVPs ) > 0:
		shotgunKVPs = tempKVPs
		UpdateShotgunUI( True )


def UpdateShotgunUI( forceOn=False ):
	global dialog
	global shotgunKVPs
	
	if shotgunKVPs != None:
		dialog.useShotgunInfo.setEnabled( len(shotgunKVPs) > 0 )
		
		if forceOn:
			dialog.useShotgunInfo.setValue( True )
		
		dialog.shotgunVersion.setValue( shotgunKVPs.get( 'VersionName', "" ) )
		dialog.shotgunVersion.setEnabled( dialog.useShotgunInfo.value() )
		dialog.shotgunDescription.setValue( shotgunKVPs.get( 'Description', "" ) )
		dialog.shotgunDescription.setEnabled( dialog.useShotgunInfo.value() )
		
		#update the draft stuff that relies on shotgun
		dialog.uploadToShotgun.setEnabled( dialog.submitDraftJob.value() and dialog.useShotgunInfo.value() )
		dialog.useShotgunDataButton.setEnabled( dialog.submitDraftJob.value() and dialog.useShotgunInfo.value() )
			
		displayText = ""
		if 'UserName' in shotgunKVPs:
			displayText += "User Name: %s\n" % shotgunKVPs[ 'UserName' ]
		if 'TaskName' in shotgunKVPs:
			displayText += "Task Name: %s\n" % shotgunKVPs[ 'TaskName' ]
		if 'ProjectName' in shotgunKVPs:
			displayText += "Project Name: %s\n" % shotgunKVPs[ 'ProjectName' ]
		if 'EntityName' in shotgunKVPs:
			displayText += "Entity Name: %s\n" % shotgunKVPs[ 'EntityName' ]	
		if 'EntityType' in shotgunKVPs:
			displayText += "Entity Type: %s\n" % shotgunKVPs[ 'EntityType' ]
		if 'DraftTemplate' in shotgunKVPs:
			displayText += "Draft Template: %s\n" % shotgunKVPs[ 'DraftTemplate' ]
			
		dialog.shotgunInfo.setValue( displayText )
	else:
		dialog.useShotgunInfo.setEnabled( False )
		dialog.useShotgunInfo.setValue( False )
	
	
def GetMachineListFromDeadline():
	global dialog
	global deadlineCommand
	
	# Get the machine list.
	try:
		stdout = os.popen( deadlineCommand + " -selectmachinelist " + dialog.machineList.value() )
		newMachineList = stdout.read()
		stdout.close()
		dialog.machineList.setValue( newMachineList.replace( "\r", "" ).replace( "\n", "" ) )
	except IOError:
		pass

def GetLimitGroupsFromDeadline():
	global dialog
	global deadlineCommand
	
	# Get the limit groups.
	try:
		stdout = os.popen( deadlineCommand + " -selectlimitgroups " + dialog.limitGroups.value() )
		newLimitGroups = stdout.read()
		stdout.close()
		dialog.limitGroups.setValue( newLimitGroups.replace( "\r", "" ).replace( "\n", "" ) )
	except IOError:
		pass

def GetDependenciesFromDeadline():
	global dialog
	global deadlineCommand
	
	# Get the dependencies
	try:
		stdout = os.popen( deadlineCommand + " -selectdependencies " + dialog.dependencies.value() )
		newDependencies = stdout.read()
		stdout.close()
		dialog.dependencies.setValue( newDependencies.replace( "\r", "" ).replace( "\n", "" ) )
	except IOError:
		pass

# Checks a path to make sure it has an extension
def HasExtension( path ):
	filename = os.path.basename( path )
	
	return filename.rfind( "." ) > -1

# Checks if path is local (c, d, or e drive).
def IsPathLocal( path ):
	lowerPath = path.lower()
	if lowerPath.startswith( "c:" ) or lowerPath.startswith( "d:" ) or lowerPath.startswith( "e:" ):
		return True
	return False

# Checks if the given filename ends with a movie extension
def IsMovie( path ):
	lowerPath = path.lower()
	if lowerPath.endswith( ".mov" ):
		return True
	return False

# Checks if the filename is padded (ie: \\output\path\filename_%04.tga).
def IsPadded( path ):
	paddingRe = re.compile( "%([0-9]+)d", re.IGNORECASE )
	if paddingRe.search( path ) != None:
		return True
	elif path.find( "#" ) > -1:
		return True
	return False

def RightReplace(s, old, new, occurrence):
	li = s.rsplit(old, occurrence)
	return new.join(li)

# Parses through the filename looking for the last padded pattern, replaces
# it with the correct number of #'s, and returns the new padded filename.
def GetPaddedPath( path ):
	#~ paddingRe = re.compile( "%([0-9]+)d", re.IGNORECASE )
	
	#~ paddingMatch = paddingRe.search( path )
	#~ if paddingMatch != None:
		#~ paddingSize = int(paddingMatch.lastgroup)
		
		#~ padding = ""
		#~ while len(padding) < paddingSize:
			#~ padding = padding + "#"
		
		#~ path = paddingRe.sub( padding, path, 1 )
	
	paddingRe = re.compile( "([0-9]+)", re.IGNORECASE )
	
	paddingMatches = paddingRe.findall( path )
	if paddingMatches != None and len( paddingMatches ) > 0:
		paddingString = paddingMatches[ len( paddingMatches ) - 1 ]
		paddingSize = len(paddingString)
		
		padding = ""
		while len(padding) < paddingSize:
			padding = padding + "#"
		
		path = RightReplace( path, paddingString, padding, 1 )
	
	return path

def WriteStickySettings( dialog, configFile ):
	global shotgunKVPs
	
	try:
		print "Writing sticky settings..."
		config = ConfigParser.ConfigParser()
		config.add_section( "Sticky" )
		
		config.set( "Sticky", "FrameListMode", dialog.frameListMode.value() )
		config.set( "Sticky", "CustomFrameList", dialog.frameList.value().strip() )
		
		config.set( "Sticky", "Department", dialog.department.value() )
		config.set( "Sticky", "Pool", dialog.pool.value() )
		config.set( "Sticky", "Group", dialog.group.value() )
		config.set( "Sticky", "Priority", str( dialog.priority.value() ) )
		config.set( "Sticky", "MachineLimit", str( dialog.machineLimit.value() ) )
		config.set( "Sticky", "IsBlacklist", str( dialog.isBlacklist.value() ) )
		config.set( "Sticky", "MachineList", dialog.machineList.value() )
		config.set( "Sticky", "LimitGroups", dialog.limitGroups.value() )
		config.set( "Sticky", "SubmitSuspended", str( dialog.submitSuspended.value() ) )
		config.set( "Sticky", "ChunkSize", str( dialog.chunkSize.value() ) )
		config.set( "Sticky", "Threads", str( dialog.threads.value() ) )
		config.set( "Sticky", "SubmitScene", str( dialog.submitScene.value() ) )
		config.set( "Sticky", "BatchMode", str( dialog.batchMode.value() ) )
		config.set( "Sticky", "ContinueOnError", str( dialog.continueOnError.value() ) )
		config.set( "Sticky", "UseNodeRange", str( dialog.useNodeRange.value() ) )
		
		config.set( "Sticky", "UseDraft", str( dialog.submitDraftJob.value() ) )
		config.set( "Sticky", "DraftTemplate", dialog.templatePath.value() )
		config.set( "Sticky", "DraftUser", dialog.draftUser.value() )
		config.set( "Sticky", "DraftEntity", dialog.draftEntity.value() )
		config.set( "Sticky", "DraftVersion", dialog.draftVersion.value() )
		
		fileHandle = open( configFile, "w" )
		config.write( fileHandle )
		fileHandle.close()
		
		
	except:
		print( "Could not write sticky settings" )

def SubmitJob( dialog, nukeFile, node, writeNodes, deadlineCommand, deadlineTemp, tempJobName, tempFrameList, tempChunkSize, jobCount, lockObj ):
    
	global shotgunJobSettings
	global shotgunKVPs
	global multiJobResults
	
	print "Preparing job #%d for submission.." % jobCount
	
	# Create a task in Nuke's progress  bar dialog
	#progressTask = nuke.ProgressTask("Submitting %s to Deadline" % tempJobName)
	progressTask = nuke.ProgressTask("Job Submission")
	progressTask.setMessage("Creating Job Info File")
	progressTask.setProgress(0)
	
	# Create the submission info file (append job count since we're submitting multiple jobs at the same time in different threads)
	jobInfoFile = deadlineTemp + ("/nuke_submit_info%d.job" % jobCount)
	fileHandle = open( jobInfoFile, "w" )
	fileHandle.write( "Plugin=Nuke\n" )
	fileHandle.write( "Name=%s\n" % tempJobName )
	fileHandle.write( "Comment=%s\n" % dialog.comment.value() )
	fileHandle.write( "Department=%s\n" % dialog.department.value() )
	fileHandle.write( "Pool=%s\n" % dialog.pool.value() )
	fileHandle.write( "Group=%s\n" % dialog.group.value() )
	fileHandle.write( "Priority=%s\n" % dialog.priority.value() )
	fileHandle.write( "MachineLimit=%s\n" % dialog.machineLimit.value() )
	fileHandle.write( "TaskTimeoutMinutes=%s\n" % dialog.taskTimeout.value() )
	fileHandle.write( "EnableAutoTimeout=%s\n" % dialog.autoTaskTimeout.value() )
	fileHandle.write( "ConcurrentTasks=%s\n" % dialog.concurrentTasks.value() )
	fileHandle.write( "LimitConcurrentTasksToNumberOfCpus=%s\n" % dialog.limitConcurrentTasks.value() )
	fileHandle.write( "LimitGroups=%s\n" % dialog.limitGroups.value() )
	fileHandle.write( "JobDependencies=%s\n" % dialog.dependencies.value() )
	fileHandle.write( "OnJobComplete=%s\n" % dialog.onComplete.value() )
	fileHandle.write( "Frames=%s\n" % tempFrameList )
	fileHandle.write( "ChunkSize=%s\n" % tempChunkSize )
	
	if dialog.submitSuspended.value():
		fileHandle.write( "InitialStatus=Suspended\n" )
	
	if dialog.isBlacklist.value():
		fileHandle.write( "Blacklist=%s\n" % dialog.machineList.value() )
	else:
		fileHandle.write( "Whitelist=%s\n" % dialog.machineList.value() )
	
	extraKVPIndex = 0
	
	if not dialog.separateJobs.value():
		index = 0
		for tempNode in writeNodes:
			if not tempNode['disable']:
				fileValue = tempNode['file']
				evaluatedValue = tempNode['file']
				
				tempPath, tempFilename = os.path.split( evaluatedValue )
				if IsPadded( os.path.basename( fileValue ) ):
					tempFilename = GetPaddedPath( tempFilename )
					
				paddedPath = os.path.join( tempPath, tempFilename )
				fileHandle.write( "OutputFilename%s=%s\n" % (index, paddedPath ) )
				index = index + 1
	else:
		fileValue = tempNode['file']
		evaluatedValue = tempNode['file']
			
		tempPath, tempFilename = os.path.split( evaluatedValue )
		if IsPadded( os.path.basename( fileValue ) ):
			tempFilename = GetPaddedPath( tempFilename )
			
		paddedPath = os.path.join( tempPath, tempFilename )
		fileHandle.write( "OutputFilename0=%s\n" % paddedPath )

	fileHandle.close()
	
	# Update task progress
	progressTask.setMessage("Creating Plugin Info File")
	progressTask.setProgress(10)
	
	# Create the plugin info file
	pluginInfoFile = deadlineTemp + ("/nuke_plugin_info%d.job" % jobCount)
	fileHandle = open( pluginInfoFile, "w" )
	if not dialog.submitScene.value():
		fileHandle.write( "SceneFile=%s\n" % nukeFile )
	
	fileHandle.write( "Version=%s.%s\n" % (nuke.env[ 'NukeVersionMajor' ], nuke.env['NukeVersionMinor']) )
	fileHandle.write( "Threads=%s\n" % dialog.threads.value() )
	fileHandle.write( "RamUse=%s\n" % dialog.memoryUsage.value() )
	fileHandle.write( "Build=%s\n" % dialog.build.value() )
	fileHandle.write( "BatchMode=%s\n" % dialog.batchMode.value())
	
	if dialog.separateJobs.value():
		#we need the fullName of the node here, otherwise write nodes that are embedded in groups won't work
		fileHandle.write( "WriteNode=%s\n" % node['name'] )
	else:
		if dialog.readFileOnly.value() or dialog.selectedOnly.value():
			writeNodesStr = ""
			
			for tempNode in writeNodes:
				if not tempNode['disable']:
					#we need the fullName of the node here, otherwise write nodes that are embedded in groups won't work
					writeNodesStr += ("%s," % tempNode['name'])
						
			writeNodesStr = writeNodesStr.strip( "," )
			fileHandle.write( "WriteNode=%s\n" % writeNodesStr )
	
	fileHandle.write( "NukeX=%s\n" % dialog.useNukeX.value() )
	fileHandle.write( "ContinueOnError=%s\n" % dialog.continueOnError.value() )
	
	fileHandle.close()
	
	# Update task progress
	progressTask.setMessage("Submitting Job to Deadline")
	progressTask.setProgress(30)
	
	# Submit the job to Deadline
	args = "\"" + jobInfoFile + "\" \"" + pluginInfoFile + "\""
	if dialog.submitScene.value():
		args += " \"" + nukeFile + "\""
	
	tempResults = ""
	
	#seems to error out when doing more than one popen at a time (in different threads), so lock our mutex var here
	lockObj.acquire()
	progressTask.setProgress(50)
	print "Lock acquired for job submission #%d" % jobCount
	try:
		stdout = os.popen( deadlineCommand + " " + args)
		tempResults = stdout.read()
		stdout.close()
	except IOError:
		tempResults = "An error occurred while submitting the job \"" + tempJobName + "\" to Deadline. Please try again, or if this is a persistent problem, contact Deadline Support."
	finally:
		#make sure we don't keep other threads waiting, release our lock...
		lockObj.release()
		print "Lock released for job submission #%d" % jobCount
	
	# Update task progress
	progressTask.setMessage("Complete!")
	progressTask.setProgress(100)
	
	print "Job submission #%d complete" % jobCount
	
	#nuke.executeInMainThread( nuke.message, tempResults )
	lockObj.acquire()
	multiJobResults += tempResults + "\n\n"
	lockObj.release()
	
	return tempResults


#This will recursively find nodes of the given class (used to find write nodes, even if they're embedded in groups).  
def RecursiveFindNodes(nodeClass, startNode):
	nodeList = []
	
	if startNode.Class() == nodeClass:
		nodeList = [startNode]
	elif isinstance(startNode, nuke.Group):
		for child in startNode.nodes():
			nodeList.extend( RecursiveFindNodes(nodeClass, child) )
		
	return nodeList

# The main submission function.
def SubmitToDeadline(currNukeScriptPath,nukeFile):
	global dialog
	global deadlineCommand
	global nukeScriptPath
	global deadlineHome
	global shotgunKVPs
	
	# Add the current nuke script path to the system path.
	nukeScriptPath = currNukeScriptPath
	sys.path.append( nukeScriptPath )
	
	# DeadlineGlobals contains initial values for the submission dialog. These can be modified
	# by an external sanity scheck script.
	import DeadlineGlobals
	
	
	# Get the deadlinecommand executable (we try to use the full path on OSX).
	deadlineCommand = "deadlinecommand"
	if os.path.exists( "/Applications/Deadline/Resources/bin/deadlinecommand" ):
		print( "Using full deadline command path" )
		deadlineCommand = "/Applications/Deadline/Resources/bin/deadlinecommand"
	
	# Get the current user Deadline home directory, which we'll use to store settings and temp files.
	deadlineHome = ""
	try:
		stdout = os.popen( deadlineCommand + " -GetCurrentUserHomeDirectory" )
		#deadlineHome = stdout.readline()
		deadlineHome = stdout.read()
		stdout.close()
	except IOError:
		nuke.message( "An error occurred while collecting the user's home directory from Deadline. Please try again, or if this is a persistent problem, contact Deadline Support." )
		return
	
	deadlineHome = deadlineHome.replace( "\n", "" )
	deadlineSettings = deadlineHome + "/settings"
	deadlineTemp = deadlineHome + "/temp"
	
	# Get the pools.
	pools = []
	try:
		stdout = os.popen( deadlineCommand + " -pools" )
		#for line in stdout:
		#	pools.append( line.replace( "\n", "" ) )
		
		output = stdout.read()
		for line in output.splitlines():
			pools.append( line.replace( "\n", "" ) )
		
		stdout.close()
	except IOError:
		nuke.message( "An error occurred while collecting the pools from Deadline. Please try again, or if this is a persistent problem, contact Deadline Support." )
		return
	
	# Get the groups.
	groups = []
	try:
		stdout = os.popen( deadlineCommand + " -groups" )
		
		#for line in stdout:
		#	groups.append( line.replace( "\n", "" ) )
		
		output = stdout.read()
		for line in output.splitlines():
			groups.append( line.replace( "\n", "" ) )
		
		stdout.close()
	except IOError:
		nuke.message( "An error occurred while collecting the groups from Deadline. Please try again, or if this is a persistent problem, contact Deadline Support." )
		return
	
	initFrameListMode = "Global"
	initCustomFrameList = None
	
	# Set initial settings for submission dialog.
	DeadlineGlobals.initJobName = os.path.basename(nukeFile)
	DeadlineGlobals.initComment = ""
	
	DeadlineGlobals.initDepartment = ""
	DeadlineGlobals.initPool = "none"
	DeadlineGlobals.initGroup = "none"
	DeadlineGlobals.initPriority = 50
	DeadlineGlobals.initTaskTimeout = 0
	DeadlineGlobals.initAutoTaskTimeout = False
	DeadlineGlobals.initConcurrentTasks = 1
	DeadlineGlobals.initLimitConcurrentTasks = True
	DeadlineGlobals.initMachineLimit = 0
	DeadlineGlobals.initIsBlacklist = False
	DeadlineGlobals.initMachineList = ""
	DeadlineGlobals.initLimitGroups = ""
	DeadlineGlobals.initDependencies = ""
	DeadlineGlobals.initOnComplete = "Nothing"
	DeadlineGlobals.initSubmitSuspended = False
	DeadlineGlobals.initChunkSize = 10
	DeadlineGlobals.initThreads = 0
	DeadlineGlobals.initMemoryUsage = 0
	
	DeadlineGlobals.initBuild = "32bit"
	if nuke.env[ '64bit' ]:
		DeadlineGlobals.initBuild = "64bit"
	
	DeadlineGlobals.initSeparateJobs = False
	DeadlineGlobals.initUseNodeRange = True
	DeadlineGlobals.initReadFileOnly = False
	DeadlineGlobals.initSelectedOnly = False
	DeadlineGlobals.initSubmitScene = False
	DeadlineGlobals.initBatchMode = False
	DeadlineGlobals.initContinueOnError = False
	
	DeadlineGlobals.initUseNukeX = False
	if nuke.env[ 'nukex' ]:
		DeadlineGlobals.initUseNukeX = True
		
	DeadlineGlobals.initUseDraft = False
	DeadlineGlobals.initDraftTemplate = ""
	DeadlineGlobals.initDraftUser = ""
	DeadlineGlobals.initDraftEntity = ""
	DeadlineGlobals.initDraftVersion = ""
	
	# Read In Sticky Settings
	configFile = deadlineSettings + "/nuke_py_submission.ini"
	print "Reading sticky settings from %s" % configFile
	try:
		if os.path.isfile( configFile ):
			config = ConfigParser.ConfigParser()
			config.read( configFile )
			
			if config.has_section( "Sticky" ):
				if config.has_option( "Sticky", "FrameListMode" ):
					initFrameListMode = config.get( "Sticky", "FrameListMode" )
				if config.has_option( "Sticky", "CustomFrameList" ):
					initCustomFrameList = config.get( "Sticky", "CustomFrameList" )
				
				if config.has_option( "Sticky", "Department" ):
					DeadlineGlobals.initDepartment = config.get( "Sticky", "Department" )
				if config.has_option( "Sticky", "Pool" ):
					DeadlineGlobals.initPool = config.get( "Sticky", "Pool" )
				if config.has_option( "Sticky", "Group" ):
					DeadlineGlobals.initGroup = config.get( "Sticky", "Group" )
				if config.has_option( "Sticky", "Priority" ):
					DeadlineGlobals.initPriority = config.getint( "Sticky", "Priority" )
				if config.has_option( "Sticky", "MachineLimit" ):
					DeadlineGlobals.initMachineLimit = config.getint( "Sticky", "MachineLimit" )
				if config.has_option( "Sticky", "IsBlacklist" ):
					DeadlineGlobals.initIsBlacklist = config.getboolean( "Sticky", "IsBlacklist" )
				if config.has_option( "Sticky", "MachineList" ):
					DeadlineGlobals.initMachineList = config.get( "Sticky", "MachineList" )
				if config.has_option( "Sticky", "LimitGroups" ):
					DeadlineGlobals.initLimitGroups = config.get( "Sticky", "LimitGroups" )
				if config.has_option( "Sticky", "SubmitSuspended" ):
					DeadlineGlobals.initSubmitSuspended = config.getboolean( "Sticky", "SubmitSuspended" )
				if config.has_option( "Sticky", "ChunkSize" ):
					DeadlineGlobals.initChunkSize = config.getint( "Sticky", "ChunkSize" )
				if config.has_option( "Sticky", "Threads" ):
					DeadlineGlobals.initThreads = config.getint( "Sticky", "Threads" )
				if config.has_option( "Sticky", "SubmitScene" ):
					DeadlineGlobals.initSubmitScene = config.getboolean( "Sticky", "SubmitScene" )
				if config.has_option( "Sticky", "BatchMode" ):
					DeadlineGlobals.initBatchMode = config.getboolean( "Sticky", "BatchMode" )
				if config.has_option( "Sticky", "ContinueOnError" ):
					DeadlineGlobals.initContinueOnError = config.getboolean( "Sticky", "ContinueOnError" )
				if config.has_option( "Sticky", "UseNodeRange" ):
					DeadlineGlobals.initUseNodeRange = config.getboolean( "Sticky", "UseNodeRange" )
					
				if config.has_option( "Sticky", "UseDraft" ):
					DeadlineGlobals.initUseDraft = config.getboolean( "Sticky", "UseDraft" )
				if config.has_option( "Sticky", "DraftTemplate" ):
					DeadlineGlobals.initDraftTemplate = config.get( "Sticky", "DraftTemplate" )
				if config.has_option( "Sticky", "DraftUser" ):
					DeadlineGlobals.initDraftUser = config.get( "Sticky", "DraftUser" )
				if config.has_option( "Sticky", "DraftEntity" ):
					DeadlineGlobals.initDraftEntity = config.get( "Sticky", "DraftEntity" )
				if config.has_option( "Sticky", "DraftVersion" ):
					DeadlineGlobals.initDraftVersion = config.get( "Sticky", "DraftVersion" )	
					
	except:
		print( "Could not read sticky settings" )
		
	#getFrames
	nukeFileFrames=scriptFirstLastFrames(nukeFile)
	
	if initFrameListMode != "Custom":
		startFrame = nukeFileFrames[0]
		endFrame = nukeFileFrames[1]

		
		if startFrame == endFrame:
			DeadlineGlobals.initFrameList = str(startFrame)
		else:
			DeadlineGlobals.initFrameList = str(startFrame) + "-" + str(endFrame)

	
	# Run the sanity check script if it exists, which can be used to set some initial values.
	sanityCheckFile = nukeScriptPath + "/CustomSanityChecks.py"
	if os.path.isfile( sanityCheckFile ):
		print( "Running sanity check script: " + sanityCheckFile )
		try:
			import CustomSanityChecks
			sanityResult = CustomSanityChecks.RunSanityCheck()
			if not sanityResult:
				print( "Sanity check returned false, exiting" )
				return
		except:
			print( "Could not run CustomSanityChecks.py script" )
	
	# Check for potential issues and warn user about any that are found.
	warningMessages = ""
	#writeNodes = RecursiveFindNodes( "Write", nuke.Root() )
	writeNodes = getWriteNodesFromScript(nukeFile)
	print writeNodes
	
	print "Found a total of %d write nodes" % len( writeNodes )
	
	
	print "Creating submission dialog..."
	
	# Create an instance of the submission dialog.
	dialog = DeadlineDialog( pools, groups )
	
	# Set the initial values.
	dialog.jobName.setValue( DeadlineGlobals.initJobName )
	dialog.comment.setValue( DeadlineGlobals.initComment )
	dialog.department.setValue( DeadlineGlobals.initDepartment )
	
	dialog.pool.setValue( DeadlineGlobals.initPool )
	dialog.group.setValue( DeadlineGlobals.initGroup )
	dialog.priority.setValue( DeadlineGlobals.initPriority )
	dialog.taskTimeout.setValue( DeadlineGlobals.initTaskTimeout )
	dialog.autoTaskTimeout.setValue( DeadlineGlobals.initAutoTaskTimeout )
	dialog.concurrentTasks.setValue( DeadlineGlobals.initConcurrentTasks )
	dialog.limitConcurrentTasks.setValue( DeadlineGlobals.initLimitConcurrentTasks )
	dialog.machineLimit.setValue( DeadlineGlobals.initMachineLimit )
	dialog.isBlacklist.setValue( DeadlineGlobals.initIsBlacklist )
	dialog.machineList.setValue( DeadlineGlobals.initMachineList )
	dialog.limitGroups.setValue( DeadlineGlobals.initLimitGroups )
	dialog.dependencies.setValue( DeadlineGlobals.initDependencies )
	dialog.onComplete.setValue( DeadlineGlobals.initOnComplete )
	dialog.submitSuspended.setValue( DeadlineGlobals.initSubmitSuspended )
	
	dialog.frameListMode.setValue( initFrameListMode )
	dialog.frameList.setValue( DeadlineGlobals.initFrameList )
	dialog.chunkSize.setValue( DeadlineGlobals.initChunkSize )
	dialog.threads.setValue( DeadlineGlobals.initThreads )
	dialog.memoryUsage.setValue( DeadlineGlobals.initMemoryUsage )
	dialog.build.setValue( DeadlineGlobals.initBuild )
	dialog.separateJobs.setValue( DeadlineGlobals.initSeparateJobs )
	dialog.readFileOnly.setValue( DeadlineGlobals.initReadFileOnly )
	dialog.selectedOnly.setValue( DeadlineGlobals.initSelectedOnly )
	dialog.submitScene.setValue( DeadlineGlobals.initSubmitScene )
	dialog.useNukeX.setValue( DeadlineGlobals.initUseNukeX )
	dialog.continueOnError.setValue( DeadlineGlobals.initContinueOnError )
	dialog.batchMode.setValue( DeadlineGlobals.initBatchMode )
	dialog.useNodeRange.setValue( DeadlineGlobals.initUseNodeRange )
	
	dialog.separateJobs.setEnabled( len( writeNodes ) > 0 )
	
	#dialog.readFileOnly.setEnabled( dialog.separateJobs.value() )
	#dialog.selectedOnly.setEnabled( dialog.separateJobs.value() )
	dialog.useNodeRange.setEnabled( dialog.separateJobs.value() )
	dialog.frameList.setEnabled( not (dialog.separateJobs.value() and dialog.useNodeRange.value()) )
	
	dialog.submitDraftJob.setValue( DeadlineGlobals.initUseDraft )
	dialog.templatePath.setValue( DeadlineGlobals.initDraftTemplate )
	dialog.draftUser.setValue( DeadlineGlobals.initDraftUser )
	dialog.draftEntity.setValue( DeadlineGlobals.initDraftEntity )
	dialog.draftVersion.setValue( DeadlineGlobals.initDraftVersion )
	
	dialog.templatePath.setEnabled( dialog.submitDraftJob.value() )
	dialog.draftUser.setEnabled( dialog.submitDraftJob.value() )
	dialog.draftEntity.setEnabled( dialog.submitDraftJob.value() )
	dialog.draftVersion.setEnabled( dialog.submitDraftJob.value() )
	
	UpdateShotgunUI()
	
	# Show the dialog.
	success = False
	while not success:
		success = dialog.ShowDialog()
		if not success:
			WriteStickySettings( dialog, configFile )
			return
		
		errorMessages = ""
		warningMessages = ""
		
		# Check that frame range is valid.
		if dialog.frameList.value().strip() == "":
			errorMessages = errorMessages + "No frame list has been specified.\n\n"
		

		
		# Check if the script file is local and not being submitted to Deadline.
		if not dialog.submitScene.value():
			if IsPathLocal( nukeFile ):
				warningMessages = warningMessages + "Nuke script path is local and is not being submitted to Deadline:\n" + nukeFile + "\n\n"
		
		# Check Draft template path
		if dialog.submitDraftJob.value():
			if not os.path.exists( dialog.templatePath.value() ):
				errorMessages += "Draft job submission is enabled, but a Draft template has not been selected (or it does not exist).  Either select a valid template, or disable Draft job submission.\n\n"
		
		# Alert the user of any errors.
		if errorMessages != "":
			errorMessages = errorMessages + "Please fix these issues and submit again."
			nuke.message( errorMessages )
			success = False
		
		# Alert the user of any warnings.
		if success and warningMessages != "":
			warningMessages = warningMessages + "Do you still wish to submit this job to Deadline?"
			answer = nuke.ask( warningMessages )
			if not answer:
				WriteStickySettings( dialog, configFile )
				return
	
	# Save sticky settings
	WriteStickySettings( dialog, configFile )
	
	tempJobName = dialog.jobName.value()
	tempFrameList = dialog.frameList.value().strip()
	tempChunkSize = dialog.chunkSize.value()
	
	global multiJobResults
	multiJobResults = ""
	submitThreads = []
	
	#setup mutex variable
	lockObj = threading.Lock()
	
	# Check if we should be submitting a separate job for each write node.
	if not dialog.separateJobs.value():
		#Create a new thread to do the submission
		print "Spawning submission thread..."
		submitThread = threading.Thread( None, SubmitJob, None, ( dialog, nukeFile, None, writeNodes, deadlineCommand, deadlineTemp, tempJobName, tempFrameList, tempChunkSize, 1, lockObj ) )
		submitThread.start()
		submitThreads.append( submitThread )
	else:
		jobCount = 0
		
		for node in writeNodes:
			print "Now processing %s" % node['name']
			#increment job count -- will be used so not all submissions try to write to the same .job files simultaneously
			jobCount += 1
			
			tempJobName = dialog.jobName.value() + " - " + node['name']
			
			#Create a new thread to do the submission
			print "Spawning submission thread #%d..." % jobCount
			submitThread = threading.Thread( None, SubmitJob, args = ( dialog, nukeFile, node, writeNodes, deadlineCommand, deadlineTemp, tempJobName, tempFrameList, tempChunkSize, jobCount, lockObj ) )
			submitThread.start()
			submitThreads.append( submitThread )
	
	print "Spawning results thread..."
	resultsThread = threading.Thread( None, WaitForSubmissions, args = ( submitThreads, ) )
	resultsThread.start()
	
	print "Main Deadline thread exiting"

def WaitForSubmissions( submitThreads ):
	for thread in submitThreads:
		thread.join()
	
	nuke.executeInMainThread( nuke.message, multiJobResults )
	
	print "Results thread exiting"

def GetRepositoryRoot():
	stdout = None
	if os.path.exists( "/Applications/Deadline/Resources/bin/deadlinecommand" ):
		stdout = os.popen( "/Applications/Deadline/Resources/bin/deadlinecommand GetRepositoryRoot" )
	else:
		stdout = os.popen(" deadlinecommand GetRepositoryRoot" )
	path = stdout.read()
	if path[-1] == '\n' :
		path = path[:-1]
	stdout.close()
	return path

def scriptFirstLastFrames(nukescript):
	fileObject=open(nukescript,"r")
	contents=fileObject.read()
	fileObject.close()
	lines=contents.split("\n")
	first=0
	last=0
	for l in lines:
		if "first_frame" in l:
			first=int(l.split("first_frame ")[-1])
		if "last_frame" in l:
			last=int(l.split("last_frame ")[-1])
	return first,last
	
	
def getWriteNodesFromScript(nukescript):
	fileObject=open(nukescript,"r")
	contents=fileObject.read()
	fileObject.close()
	writes=contents.split("Write {")[1:]
	nodes=[]
	for wr in writes:
		writeDict={}
		writeDict['name']=""
		writeDict['disable']=False
		writeDict['file']=""
		for line in wr.split("\n")[:15]:
			if "name " in line and writeDict['name']=="":
				writeDict['name']=line.split("name ")[-1]
			if "disable" in line:
				writeDict['disable']=True
			if "file " in line and writeDict['file']=="":
				writeDict['file']=line.split("file ")[-1]
		nodes.append(writeDict)
	return nodes
		
################################################################################
## DEBUGGING
################################################################################
#~ # Get the repository root
#~ try:
	#~ path = GetRepositoryRoot()
	
	#~ if path == "" or path == None:
		#~ nuke.message( "The SubmitNukeToDeadline.py script could not be found in the Deadline Repository. Please make sure that the Deadline Client has been installed on this machine, that the Deadline Client bin folder is in your PATH, and that the Deadline Client has been configured to point to a valid Repository." )
	#~ else:
		#~ path += "/submission/Nuke"
		#~ path = path.replace("\n","").replace( "\\", "/" )
		
		#~ # Add the path to the system path
		#~ print( "Appending \"" + path + "\" to system path to import SubmitNukeToDeadline module" )
		#~ sys.path.append( path )
		
		#~ # Call the main function to begin job submission.
		#~ SubmitToDeadline( path )
#~ except IOError:
	#~ nuke.message( "An error occurred while getting the repository root from Deadline. Please try again, or if this is a persistent problem, contact Deadline Support." )
	