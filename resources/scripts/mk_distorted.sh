#!/bin/bash

# Created by argbash-init v2.1.1
# ARG_OPTIONAL_SINGLE([transform],[t],[The transformation defined by coefficients and center coords],[0,-0.005,-0.05,1.055,300,300])
# ARG_HELP([The distortion calculator])
# ARGBASH_GO()
# needed because of Argbash --> m4_ignore([
### START OF CODE GENERATED BY Argbash v2.1.1 one line above ###
# Argbash is a bash code generator used to get arguments parsing right.
# Argbash is FREE SOFTWARE, know your rights: https://github.com/matejak/argbash

die()
{
	local _ret=$2
	test -n "$_ret" || _ret=1
	test "$_PRINT_HELP" = yes && print_help >&2
	echo "$1" >&2
	exit ${_ret}
}
# validators

# THE DEFAULTS INITIALIZATION - OPTIONALS
_arg_transform="0,-0.005,-0.05,1.055,300,300"

# THE PRINT HELP FUNCION
print_help ()
{
	echo "The distortion calculator"
	printf 'Usage: %s [-t|--transform <arg>] [-h|--help]\n' "$0"
	printf "\t-t,--transform: The transformation defined by coefficients and center coords (default: '%s')\n" "0,-0.005,-0.05,1.055,300,300"
	printf "\t-h,--help: Prints help\n"
}

# THE PARSING ITSELF
while test $# -gt 0
do
	_key="$1"
	case "$_key" in
		-t|--transform|--transform=*)
			_val="${_key##--transform=}"
			if test "$_val" = "$_key"
			then
				test $# -lt 2 && die "Missing value for the optional argument '$_key'." 1
				_val="$2"
				shift
			fi
			_arg_transform="$_val"
			;;
		-h|--help)
			print_help
			exit 0
			;;
		*)
			_PRINT_HELP=yes die "FATAL ERROR: Got an unexpected argument '$1'" 1
			;;
	esac
	shift
done

# OTHER STUFF GENERATED BY Argbash

### END OF CODE GENERATED BY Argbash (sortof) ### ])
# [ <-- needed because of Argbash


for idx in 00 01
do
	python ../../mk_transform.py ../patterns/lines-${idx#0}.png "$_arg_transform" ../../distorted-$idx.png
done

# ] <-- needed because of Argbash
