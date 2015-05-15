#! /bin/bash

USAGE='sesame.sh {e|d} [-h]

Encrypt/decrypt files and directories with a tar-like interface.

  e     encrypt
  d     decrypt
  -h    show help message and exit'

USAGE_E='sesame.sh e [-h] [-p password]
                     [outputfile] filepath [filepath ...]

positional arguments:
  outputfile            encrypted output filename (will default if only
                        encrypting one file)
  inputfile             file(s) to be encrypted

optional arguments:
  -h                    show this help message and exit
  -p PASSWORD           encryption password
  -f                    force overwrite of existing encrypted file'

USAGE_D='sesame.sh d [-h] [-p password] [-f] [-O OUTPUT_DIR] inputfile

positional arguments:
  inputfile             file to be decrypted

optional arguments:
  -h                    show this help message and exit
  -p PASSWORD           decryption password
  -f                    force overwrite of existing decrypted file(s)'

if [[ $# -eq 0 ]]; then
	echo "$USAGE"
	exit 1
fi

# either 'e' for encrypt or 'd' for decrypt
COMMAND=$1
shift

if [[ $COMMAND != 'e' && $COMMAND != 'd' ]]; then
	echo "$USAGE"
	exit 1
fi

PASSWORD=''
FORCE=0
HELP=0

while getopts 'hp:f' options
do
	case $options in
	h ) HELP=1;;
	p ) PASSWORD="$OPTARG";;
	f ) FORCE=1;;
	esac
done
shift $((OPTIND-1))


# handle -h flag
if [[ $HELP -eq 1 ]]; then
	if [[ $COMMAND = 'e' ]]; then
		echo "$USAGE_E"
	elif [[ $COMMAND = 'd' ]]; then
		echo "$USAGE_D"
	else
		echo "$USAGE"
	fi
	exit 1
fi

if [[ $COMMAND = 'e' ]]; then
	# encrypt
	# first parameter is the output filename
	# remaining parameters are files to encrypt
	OUTPUTFILE="$1"

	# if only encrypting a single file (meaning num args == 1), 
	# outputfile and inputfiles are both param $1. In this case, append
	# .sesame to create a new output filename.
	# If multiple paths supplied, assume the first is the output filename,
	# and shift it off the start of the args list
	if [[ $# -eq 1 ]]; then
		# append .sesame suffix if not already existent
		if [[ ${#OUTPUTFILE} -lt 9 ]]; then
			OUTPUTFILE="${OUTPUTFILE}.sesame"

		elif [[ ${OUTPUTFILE:$((${#OUTPUTFILE}-7)):7} != '.sesame' ]]; then
			OUTPUTFILE="${OUTPUTFILE}.sesame"
		fi

		echo "Defaulting to ${OUTPUTFILE} as output filename"
	else
		shift
	fi

else
	# decrypt
	# first parameter is the file to decrypt
	INPUTFILE="$1"
fi

# validate all input file paths
END=0
for P in "$@"; do
	if [[ ! -f "$P" && ! -d "$P" ]]; then
		echo "Path not valid: $P"
		END=1
	fi
done

# exit on path validation error
if [[ $END -ne 0 ]]; then
	exit $END
fi


function check_exists {
	# check output file already exists
	if [[ -f $1 || -d $1 ]]; then
		read -t 5 -p "File exists at ${1}. Overwrite? [y/N] " -n1 -s
		if [[ $? -gt 0 ]]; then
			printf '\nAborted on timeout\n'
			return 4
		fi
		echo ''
	else
		REPLY=y
	fi

	# abort if not overwriting
	if [[ $REPLY =~ ^[Nn]$ ]]; then
		return 3
	fi
}


function encrypt {
	local OUTPUTFILE="$1"
	local PASSWORD="$2"
	local FORCE="$3"
	shift 3

	# all input paths are tarballed first
	tar czf "$TMPDIR/sesame.tar" "$@" 1>/dev/null 2>&1

	if [[ $? -gt 0 ]]; then
		return $?
	fi

	if [[ $FORCE -eq 0 ]]; then
		# check output file does not already exist
		check_exists "$OUTPUTFILE" || return $?
	fi

	# encrypt the tarball
	if [[ -z $PASSWORD ]]; then
		openssl cast5-cbc -e \
			-in "$TMPDIR/sesame.tar" \
			-out "$OUTPUTFILE"
	else
		openssl cast5-cbc -e \
			-k "$PASSWORD" \
			-in "$TMPDIR/sesame.tar" \
			-out "$OUTPUTFILE"
	fi
}


function decrypt {
	local INPUTFILE="$1"
	local PASSWORD="$2"
	local FORCE="$3"
	shift 3

	# decrypt the input file
	if [[ -z $PASSWORD ]]; then
		openssl cast5-cbc -d \
			-in "$INPUTFILE" \
			-out "$TMPDIR/sesame.tar"
	else
		openssl cast5-cbc -d \
			-k "$PASSWORD" \
			-in "$INPUTFILE" \
			-out "$TMPDIR/sesame.tar"
	fi

	if [[ $? -gt 0 ]]; then
		return $?
	fi

	if [[ $FORCE -eq 0 ]]; then
		# check all paths to ensure they don't already exist
		for P in $(tar tf "$TMPDIR/sesame.tar"); do
			check_exists "$P" || return $?
		done
	fi

	# all encrypted files are tarballs; untar it
	tar xzf "$TMPDIR/sesame.tar" 1>/dev/null 2>&1
}


# create a temporary working dir
TMPDIR=$(mktemp -dt 'sesame')

if [[ $COMMAND = 'e' ]]; then
	encrypt "$OUTPUTFILE" "$PASSWORD" "$FORCE" "$@"
else
	decrypt "$INPUTFILE" "$PASSWORD" "$FORCE" "$@"
fi

# exit with return code from encrypt/decrypt
exit $?

# clean up the tmp dir
trap 'rm -rf "$TMPDIR"' EXIT
