#!/usr/bin/env python3
# -*- mode: python -*-
# Copyright © 2018 Johannes Thumshirn
# Licensed under the GPLv2

from . import MMHelper

class x86_64(MMHelper):
    PAGE_OFFSET = 0xffff880000000000  # 4-Level page tables
    START_KERNEL_MAP = 0xffffffff80000000
    PHYS_BASE = 0x0000000000000000
    PGDIR_SHIFT = 48
    PTRS_PER_PGD = 512
    PHYSICAL_MASK_SHIFT = 44
    PHYSICAL_MASK = (1 << PHYSICAL_MASK_SHIFT)
    PAGE_SHIFT = 12
    PAGE_SIZE = (1 << PAGE_SHIFT)
    PAGE_MASK = ~(PAGE_SIZE - 1)
    PHYSICAL_PAGE_MASK = (PAGE_MASK & PHYSICAL_MASK)
    P4D_SHIFT = 39
    PTRS_PER_P4D = 512
    PUD_SHIFT = 30
    PTRS_PER_PUD = 512
    PTE_PFN_MASK = PHYSICAL_PAGE_MASK
    PUD_PAGE_SIZE = (1 << PUD_SHIFT)
    PUD_PAGE_MASK = ~(PUD_PAGE_SIZE - 1)
    PHYSICAL_PUD_PAGE_MASK = (PUD_PAGE_MASK & PHYSICAL_MASK)
    PAGE_BIT_PSE = 7
    PAGE_PSE = 1 << PAGE_BIT_PSE
    PMD_SHIFT = 21
    PTRS_PER_PMD = 512

    def __init__(self):
        pass

    def __va(self, x):
        x = x + self.PAGE_OFFSET
        return x & 0xffffffffffffffff

    def __pa(self, x):
        """ arch/x86/mm/physaddr.c#L14 """
        y = x - self.START_KERNEL_MAP

        if x > y:
            x = y + self.PHYS_BASE
        else:
            x = y + (self.START_KERNEL_MAP - self.PAGE_OFFSET)

        return x & 0xffffffffffffffff

    def phys_to_virt(self, address):
        return self.__va(address)

    def virt_to_phys(self, address):
        return self.__pa(address)

    def pgd_index(self, address):
        """ arch/x86/include/asm/pgtable.h#L912 """
        return ((address) >> self.PGDIR_SHIFT) & (self.PTRS_PER_PGD - 1)

    def pgd_page_vaddr(self, pgd):
        return self.__va(pgd & self.PTE_PFN_MASK)

    def p4d_index(self, address):
        return (address >> self.P4D_SHIFT) & (self.PTRS_PER_P4D - 1)

    def p4d_offset(self, pgd, address):
        return self.pgd_page_vaddr(pgd) + self.p4d_index(address)

    def pud_index(self, address):
        return (address >> self.PUD_SHIFT) & (self.PTRS_PER_PUD - 1)

    def p4d_page_vaddr(self, p4d):
        return self.__va(p4d & self.PTE_PFN_MASK)

    def pud_offset(self, p4d, address):
        return self.p4d_page_vaddr(p4d) + self.pud_index(address)

    def pud_pfn_mask(self, pud):
        if pud & self.PAGE_PSE:
            return self.PHYSICAL_PUD_PAGE_MASK
        else:
            return self.PTE_PFN_MASK

    def pud_page_vaddr(self, pud):
        return self.__va(pud & self.pud_pfn_mask(pud))

    def pmd_offset(self, pud, address):
        return self.pud_page_vaddr(pud) + self.pmd_index(address)

    def pmd_index(self, address):
        return (address >> self.PMD_SHIFT) & (self.PTRS_PER_PMD - 1)

    def dump_pagetable(self, address, cr3):
        """ arch/x86/mm/fault.c#L368 """
        base = self.__va(cr3)
        pgd = base + self.pgd_index(address)
        p4d = self.p4d_offset(pgd, address)
        pud = self.pud_offset(p4d, address)
        pmd = self.pmd_offset(pud, address)

        print("address: " + hex(address))
        print("cr3: " + hex(cr3))
        print("pgd: " + hex(pgd))
        print("p4d: " + hex(p4d))
        print("pud: " + hex(pud))
        print("pmd: " + hex(pmd))
