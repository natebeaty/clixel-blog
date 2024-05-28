---
title: "Getting US Timezones From Zipcodes in PHP Without an API"
date: 2024-03-28
slug: "getting-us-timezones-from-zipcodes-in-php-without-an-api"
---

A client wanted to batch update a customer database with timezones so their sales team could have a better idea when best to harass folks by phone. Looking for solutions to determine timezones from an address really sent me down a rabbit hole. Stack Overflow has answers that go all over the place over the last decade plus, most of them coming down to using Google Maps API, or Nominatim/OpenStreetMap via geopy in python. The first step is to determine latitude and longitude, and then either make another API call to get timezone, or some manner of querying via boundary maps. Another solution I found was to have a giant SQL table of zipcode to timezone lookups, but it was out of date, and required quite a bit of storage for such a simple task.

I really didn't need extreme accuracy, so I figured using zipcodes would be ideal. I found an old, abandoned-but-oft-forked [Ruby gem, TZip](https://github.com/farski/TZip) which did just this, and without any external API requirements. I seem to keep finding abandoned Ruby libraries that are *almost* perfect solutions to obscure requirements I have, like the [ONIX gem that I forked and hacked away at myself](https://github.com/natebeaty/onix), which I used in a [simple Sinatra app](https://github.com/natebeaty/onix-sinatra) to convert book data in JSON to ugly ONIX XML.

When I peeked under the hood, I realized this Ruby library would be easy to adapt to PHP, so I could keep from having another decoupled service running that needed updating separate from my behemoth custom PHP codebase. I ended up refactoring output to match the terminology my client requested ("Eastern" instead of "America/Eastern").

Usage: 

```
$timezone = new Timezone();
echo $timezone->findTimezone(27705);
// 'Eastern'
```

I haven't heard any complaints after using this for over a year, so I think it's as accurate as needed! Hopefully it's of use to someone else.

Revisiting this post (which I originally started writing in early 2023, egads), I had to track down the Ruby library I mentioned, and in doing so found [a newer Ruby gem, Ziptz](https://github.com/infused/ziptz) that would do the trick if you need this in Ruby.

```
/**
 * Timezone lookups based on ZIP code
 */
class Timezone {

  // Zonings and mappings for determining timezone as accurately as possible
  public $zonings = [];
  public $mappings = [];

  /**
   * Init
   */
  public function __construct() {
    $this->zonings['Alaska'] = explode(' ', '995 996 997 998 999');
    $this->zonings['Central'] =  explode(' ', '35 36 370 3720 3723 381 383 39');
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '4641'));
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '50 51 52 53 54 55 56 57 581 582 585'));
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '60 61 62 63 64 65 660 661 6660 672 680 681 685'));
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '7'));
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '371 372 373 375 377 380 382 384 385 386 387 388 389 401 420 421 422 423 424 426 427 498 498 499 580 583 584 587 588 662 664 665 666 667 668 669 670 671 673 674 675 676 677 678 679 683 684 686 687 688 689 690 691 692'));
    # Indiana zip prefixes span Eastern/Central timezones so the full 5 digits is needed
    $this->zonings['Central'] = array_merge($this->zonings['Central'], explode(' ', '47514 47515 47520 47525 47551 47574 47576 47586 47588 46301 46302 46303 46304 46307 46308 46310 46311 46312 46319 46320 46321 46322 46323 46324 46325 46327 46340 46342 46345 46346 46347 46348 46349 46350 46352 46355 46356 46360 46361 46365 46368 46371 46372 46373 46375 46376 46377 46379 46380 46381 46382 46383 46384 46385 46390 46391 46392 46393 46394 46366 46401 46402 46403 46404 46405 46407 46409 46531 46534 46968 46341 46374 46532 46552 47523 47537 47577 47601 47639 47640 47660 47943 47948'));

    $this->zonings['Eastern'] = explode(' ', '0 1 2');
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '30 31 32 33 34 376 379 398 399'));
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '402 405 410 43 44 45 460 462 462 480 481 482 483 485 488 489 490 495 496 '));
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '569'));
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '021 034 037 038 040 041 042 046 047 048 049 053 056 058 063 064 066 067 068 069 070 074 077 085 086 088 373 374 377 378 400 401 403 404 407 408 409 411 412 413 414 415 417 418 484 486 487 491 492 493 494 497 498 499'));
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '400 401 403 404 406 407 408 409 411 412 413 414 415 416 417 418 420 421 422 423 424 425 426 427'));
    # Indiana zip prefixes span Eastern/Central timezones so the full 5 digits is needed
    $this->zonings['Eastern'] = array_merge($this->zonings['Eastern'], explode(' ', '46112 46113 46121 46124 46130 46133 46148 46158 46160 46164 46180 46181 46186 46406 46408 46506 46511 46550 46562 46574 46705 46723 46725 46732 46747 46761 46767 46770 46776 46783 46788 46792 46910 46919 46929 46940 46950 46960 46970 46982 46991 47001 47006 47018 47040 47041 47060 47106 47118 47122 47125 47138 47140 47147 47170 47177 47224 47230 47232 47235 47244 47250 47264 47272 47281 47325 47336 47352 47354 47359 47368 47373 47384 47432 47433 47436 47438 47448 47456 47468 47513 47532 47553 47833 47834 47837 47842 47858 47868 47874 47917 47918 47926 47932 47952 47960 47970 46102 46103 46104 46105 46106 46107 46110 46111 46115 46117 46118 46120 46122 46123 46125 46126 46127 46128 46129 46131 46135 46140 46142 46143 46144 46146 46147 46149 46150 46151 46154 46155 46156 46157 46161 46162 46163 46165 46166 46167 46168 46170 46171 46172 46173 46175 46176 46182 46183 46184 46501 46502 46504 46507 46508 46510 46513 46514 46515 46516 46517 46524 46526 46527 46528 46530 46536 46537 46538 46539 46540 46542 46543 46544 46545 46546 46553 46554 46555 46556 46561 46563 46565 46567 46570 46571 46572 46573 46580 46581 46582 46590 46595 46601 46613 46614 46615 46616 46617 46619 46624 46626 46628 46634 46635 46637 46660 46680 46699 46701 46702 46703 46704 46706 46710 46711 46713 46714 46721 46730 46731 46733 46737 46738 46740 46741 46742 46743 46745 46746 46748 46750 46755 46759 46760 46763 46764 46765 46766 46769 46771 46772 46773 46774 46777 46778 46779 46780 46781 46782 46784 46785 46786 46787 46789 46791 46793 46794 46795 46796 46797 46798 46799 46801 46802 46803 46804 46805 46806 46807 46808 46809 46814 46815 46816 46818 46819 46825 46835 46845 46850 46851 46852 46853 46854 46855 46856 46857 46858 46859 46860 46861 46862 46863 46864 46865 46866 46867 46868 46869 46885 46895 46896 46897 46898 46899 46901 46902 46903 46904 46911 46912 46913 46914 46915 46916 46917 46920 46921 46922 46923 46926 46928 46930 46931 46932 46933 46935 46936 46937 46938 46939 46941 46942 46943 46945 46946 46947 46951 46952 46953 46957 46958 46959 46961 46962 46965 46967 46971 46974 46975 46977 46978 46979 46980 46984 46986 46987 46988 46989 46990 46992 46994 46995 46998 47003 47010 47012 47016 47017 47021 47022 47023 47024 47025 47030 47031 47032 47033 47034 47035 47036 47037 47039 47042 47102 47104 47107 47108 47110 47111 47112 47114 47115 47117 47119 47120 47124 47126 47129 47130 47131 47132 47133 47134 47135 47136 47141 47142 47143 47144 47146 47150 47151 47160 47161 47162 47163 47164 47165 47166 47167 47172 47190 47199 47201 47202 47203 47220 47223 47225 47226 47227 47228 47229 47231 47234 47236 47240 47243 47245 47246 47247 47249 47260 47261 47263 47265 47270 47273 47274 47280 47282 47283 47302 47303 47304 47305 47306 47307 47308 47320 47322 47324 47326 47327 47330 47331 47334 47335 47337 47338 47339 47340 47341 47342 47344 47345 47346 47348 47351 47353 47355 47356 47357 47358 47360 47361 47362 47366 47367 47369 47370 47371 47374 47375 47380 47381 47382 47383 47385 47386 47387 47388 47390 47392 47393 47394 47396 47401 47402 47403 47404 47405 47406 47407 47408 47420 47421 47424 47426 47427 47429 47431 47434 47435 47437 47439 47441 47443 47445 47446 47449 47451 47452 47453 47454 47455 47458 47459 47460 47462 47463 47464 47465 47467 47469 47470 47471 47531 47536 47550 47552 47556 47579 47610 47611 47612 47613 47615 47616 47617 47618 47619 47620 47629 47630 47631 47633 47634 47635 47637 47638 47647 47648 47649 47654 47665 47666 47670 47683 47701 47702 47703 47704 47705 47706 47708 47710 47711 47712 47713 47714 47715 47716 47719 47720 47721 47722 47724 47725 47728 47730 47731 47732 47733 47734 47735 47736 47737 47740 47747 47750 47801 47802 47803 47804 47805 47807 47808 47809 47830 47831 47832 47836 47838 47840 47841 47845 47846 47847 47848 47849 47850 47851 47852 47853 47854 47855 47857 47859 47860 47861 47862 47863 47865 47866 47869 47870 47871 47872 47875 47876 47878 47879 47880 47881 47882 47884 47885 47901 47902 47903 47904 47905 47906 47907 47909 47916 47920 47921 47922 47923 47924 47925 47928 47929 47930 47933 47940 47941 47942 47944 47949 47950 47951 47954 47955 47958 47959 47962 47963 47964 47965 47966 47967 47968 47969 47971 47974 47975 47977 47978 47980 47981 47982 47983 47984 47986 47987 47988 47989 47990 47991 47992 47993 47994 47995 47996 47997 47116 47123 47137 47145 47174 47175 47457 47501 47512 47516 47519 47521 47522 47524 47527 47528 47529 47535 47541 47542 47545 47546 47547 47549 47557 47558 47561 47562 47568 47573 47575 47578 47580 47581 47591 47596 47597 47564 47567 47584 47585 47590 47598 46985 46996 47946 47957 47011 47019 47020 47038 47043'));

    $this->zonings['Hawaii'] = explode(' ', '967 968');

    $this->zonings['Mountain'] = explode(' ', '577');
    $this->zonings['Mountain'] = array_merge($this->zonings['Mountain'], explode(' ', '59'));
    $this->zonings['Mountain'] = array_merge($this->zonings['Mountain'], explode(' ', '798 799'));
    $this->zonings['Mountain'] = array_merge($this->zonings['Mountain'], explode(' ', '80 81 82 83 831 84 8501 87 88'));
    $this->zonings['Mountain'] = array_merge($this->zonings['Mountain'], explode(' ', '979'));
    $this->zonings['Mountain'] = array_merge($this->zonings['Mountain'], explode(' ', '586 677 678 690 691 692 693'));

    $this->zonings['Pacific'] = explode(' ', '835 838 889 89');
    $this->zonings['Pacific'] = array_merge($this->zonings['Pacific'], explode(' ', '90 91 92 93 94 95 960 961 962 963 964 965 969 972 973 975 977 98 990 991 992 993 994'));
    $this->zonings['Pacific'] = array_merge($this->zonings['Pacific'], explode(' ', '970 971 974 976 978'));
    $this->zonings['Pacific'] = array_merge($this->zonings['Pacific'], explode(' ', '85 86')); // Arizona

    $this->zonings['Unused'] = explode(' ', '000 002 003 004 099');
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '213 269'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '343 348 353'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '419 429'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '517 518 519 529 533 536 552 568 578 579 589'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '621 632 642 643 659 663 682 694 695 696 697 698 699'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '702 709 715 732 742 771'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '817 818 819 839 848 849 854 858 861 862 866 867 868 869 876 886 887 888 892 896 899'));
    $this->zonings['Unused'] = array_merge($this->zonings['Unused'], explode(' ', '909 929 987'));

    // Create lookup array for determining timezone
    foreach ($this->zonings as $zone => $prefixes) {
      foreach ($prefixes as $prefix) {
        $this->mappings[$prefix] = $zone;
      }
    }
  }

  /**
   * Find timezone for a ZIP code
   */
  public function findTimezone($zipcode) {
    $zipcode = substr(trim($zipcode), 0, 5);
    // Loop through levels of specificity to try finding a timezone
    foreach([5,4,3,2,1] as $i) {
      $chk = substr($zipcode, 0, $i);
      if (array_key_exists($chk, $this->mappings)) {
        if ($this->mappings[$chk] == 'Unused')
          return '';
        else
          return $this->mappings[$chk];
      }
    }
    return '';
  }

}
```
