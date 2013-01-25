_blenderCave() {
    local args cur opts

    COMPREPLY=()

    argc=${COMP_CWORD}

    cur="${COMP_WORDS[argc]}"

    case $argc in
	1)
	    opts="start startalone stop stopalone version"
	    COMPREPLY=( $(compgen -W "$opts" -- $cur ) )
	    ;;
	2)
	    prev="${COMP_WORDS[argc-1]}"
	    if [ "$prev" == "start" -o "$prev" == "startalone" ]; then
		COMPREPLY=( $(compgen -d -S / $cur) $(compgen -f -X "!*.blend" $cur ) )
	    fi
	    ;;
    esac


}

complete -F _blenderCave BlenderCave.py